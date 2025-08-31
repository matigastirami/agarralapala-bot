import logging
import time
import signal
import sys
import os
import subprocess
import requests
from threading import Thread

from flask import Flask
from bot.telegram_bot import TelegramBot
from crons.cron_manager import CronManager
from crons.job_seeker_cron import JobSeekerCron
from crons.job_enrichment_cron import JobEnrichmentCron
from crons.notification_cron import NotificationCron
from crons.match_notification_cron import MatchNotificationCron

# Global variables for graceful shutdown
cron_manager = None
telegram_bot = None
shutdown_requested = False

# Create Flask app for health checks
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return {'status': 'healthy', 'service': 'jobs-agent'}, 200

@app.route('/')
def root():
    """Root endpoint"""
    return {'message': 'Jobs Agent Telegram Bot', 'status': 'running'}, 200

def check_existing_processes():
    """Check for existing main.py processes that might cause conflicts"""
    try:
        # Check for other main.py processes
        result = subprocess.run(
            ['pgrep', '-f', 'python.*main.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            current_pid = os.getpid()
            
            # Filter out current process
            other_pids = [pid for pid in pids if pid and int(pid) != current_pid]
            
            if other_pids:
                logging.warning(f"Found existing main.py processes with PIDs: {other_pids}")
                logging.warning("This may cause Telegram bot conflicts!")
                logging.warning("Consider killing these processes before starting.")
                return True
        
        return False
        
    except Exception as e:
        logging.warning(f"Could not check for existing processes: {e}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logging.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True

def cleanup():
    """Clean up resources before exit"""
    global cron_manager, telegram_bot
    
    logging.info("Cleaning up resources...")
    
    if cron_manager:
        try:
            cron_manager.shutdown()
            logging.info("Cron manager shutdown completed")
        except Exception as e:
            logging.error(f"Error shutting down cron manager: {e}")
    
    if telegram_bot:
        try:
            # Stop the telegram bot polling
            telegram_bot.app.stop()
            logging.info("Telegram bot stopped")
        except Exception as e:
            logging.error(f"Error stopping telegram bot: {e}")
    
    logging.info("Cleanup completed")

def run_flask():
    """Run Flask app in a separate thread"""
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_keep_alive():
    """Send periodic keep-alive requests to prevent Render from sleeping"""
    # Wait for Flask to start up
    time.sleep(30)
    
    port = int(os.environ.get('PORT', 8000))
    health_url = f"http://localhost:{port}/health"
    interval = 14 * 60  # 14 minutes in seconds
    
    logging.info(f"Starting keep-alive service, pinging {health_url} every {interval/60} minutes")
    
    while not shutdown_requested:
        try:
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                logging.info("Keep-alive ping successful")
            else:
                logging.warning(f"Keep-alive ping returned status: {response.status_code}")
        except Exception as e:
            logging.warning(f"Keep-alive ping failed: {e}")
        
        # Sleep in small increments to check for shutdown
        for _ in range(interval):
            if shutdown_requested:
                break
            time.sleep(1)

# if __name__ == '__main__':
#     if len(sys.argv) <= 1:
#         raise Exception('You must enter a prompt')
#     message = sys.argv[1]
#     job_postings = exec_jobs_agent(user_input=message)
#     job_postings_repo = JobPostingsRepository()
#     job_postings_repo.save_job_postings(job_postings)


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check for existing processes that might cause conflicts
    if check_existing_processes():
        logging.warning("Continuing anyway, but conflicts may occur...")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logging.info("Starting jobs-agent application...")
        
        # Start Flask health check server in a separate thread
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logging.info("Flask health check server started")
        
        # Start keep-alive service in a separate thread
        keep_alive_thread = Thread(target=run_keep_alive, daemon=True)
        keep_alive_thread.start()
        logging.info("Keep-alive service started")
        
        # Initialize cron manager
        cron_manager = CronManager()
        
        # Register all cron jobs
        cron_manager.register(JobSeekerCron())  # Original job fetching
        cron_manager.register(JobEnrichmentCron())  # New enrichment workflow
        cron_manager.register(NotificationCron())  # New notification system
        cron_manager.register(MatchNotificationCron())  # Daily match notifications
        
        cron_manager.start()
        logging.info("Cron manager started successfully")

        # Initialize and start telegram bot with retry mechanism
        telegram_bot = TelegramBot()
        logging.info("Telegram bot initialized, starting polling...")
        
        # Retry mechanism for telegram bot conflicts with exponential backoff
        max_retries = 8
        base_delay = 60  # Start with 60 seconds
        
        for attempt in range(max_retries):
            try:
                # Start the bot in a way that allows for graceful shutdown
                telegram_bot.app.run_polling(
                    allowed_updates=[],
                    drop_pending_updates=True,  # Drop any pending updates on startup
                    close_loop=False  # Don't close the loop automatically
                )
                logging.info("Telegram bot started successfully")
                break
                
            except Exception as e:
                error_str = str(e).lower()
                if any(conflict_indicator in error_str for conflict_indicator in [
                    "terminated by other getupdates request",
                    "conflict",
                    "getupdates",
                    "another instance"
                ]):
                    if attempt < max_retries - 1:
                        # Exponential backoff: 60s, 120s, 240s, 480s, etc.
                        retry_delay = base_delay * (2 ** attempt)
                        logging.warning(f"Telegram bot conflict detected (attempt {attempt + 1}/{max_retries})")
                        logging.info(f"Waiting {retry_delay} seconds before retry... (exponential backoff)")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logging.error("Max retries reached for telegram bot. Exiting.")
                        raise
                else:
                    logging.error(f"Unexpected error starting telegram bot: {e}")
                    raise

        # Main loop with graceful shutdown
        while not shutdown_requested:
            time.sleep(1)
            
    except Exception as e:
        logging.error(f"Fatal error in main application: {e}")
        sys.exit(1)
        
    finally:
        cleanup()
        logging.info("Application shutdown completed")
