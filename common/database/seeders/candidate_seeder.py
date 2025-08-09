from common.database.database import db_session
from common.database.models.candidate import Candidate
from sqlalchemy.orm import Session


class CandidateSeeder:
    def __init__(self):
        self.session: Session = db_session()

    def seed(self):
        """Seed the database with 10 candidates"""
        candidates_data = [
            {
                "tech_stack": "NestJS, TypeScript, Node.js, PostgreSQL, Docker",
                "role": "backend",
                "location": "Buenos Aires, Argentina",
                "language": "es"
            },
            {
                "tech_stack": "React, TypeScript, Next.js, Tailwind CSS, Redux",
                "role": "frontend",
                "location": "Santiago, Chile",
                "language": "es"
            },
            {
                "tech_stack": "Python, Django, FastAPI, PostgreSQL, AWS",
                "role": "backend",
                "location": "Bogotá, Colombia",
                "language": "es"
            },
            {
                "tech_stack": "Vue.js, JavaScript, Nuxt.js, Vuetify, Pinia",
                "role": "frontend",
                "location": "Lima, Peru",
                "language": "es"
            },
            {
                "tech_stack": "Python, Pandas, NumPy, Scikit-learn, Jupyter",
                "role": "data",
                "location": "Montevideo, Uruguay",
                "language": "es"
            },
            {
                "tech_stack": "Java, Spring Boot, Hibernate, MySQL, Maven",
                "role": "backend",
                "location": "São Paulo, Brazil",
                "language": "pt"
            },
            {
                "tech_stack": "Angular, TypeScript, RxJS, Material UI, NgRx",
                "role": "frontend",
                "location": "Mexico City, Mexico",
                "language": "es"
            },
            {
                "tech_stack": "Python, TensorFlow, PyTorch, Apache Spark, Airflow",
                "role": "data",
                "location": "Buenos Aires, Argentina",
                "language": "es"
            },
            {
                "tech_stack": "Go, Gin, GORM, Redis, Kubernetes",
                "role": "backend",
                "location": "Santiago, Chile",
                "language": "es"
            },
            {
                "tech_stack": "React Native, TypeScript, Expo, Firebase, Redux Toolkit",
                "role": "frontend",
                "location": "Bogotá, Colombia",
                "language": "es"
            }
        ]

        print("🌱 Seeding candidates...")
        
        seeded_count = 0
        for i, candidate_data in enumerate(candidates_data, 1):
            # Check if candidate already exists (by tech_stack and role combination)
            existing_candidate = self.session.query(Candidate).filter_by(
                tech_stack=candidate_data["tech_stack"],
                role=candidate_data["role"]
            ).first()
            
            if existing_candidate:
                print(f"⚠️  Candidate {i} already exists, skipping...")
                continue
            
            candidate = Candidate(
                tech_stack=candidate_data["tech_stack"],
                role=candidate_data["role"],
                location=candidate_data["location"],
                language=candidate_data["language"]
            )
            
            self.session.add(candidate)
            seeded_count += 1
            print(f"✅ Created candidate {i}: {candidate_data['role']} developer from {candidate_data['location']}")

        try:
            self.session.commit()
            print(f"🎉 Successfully seeded {seeded_count} candidates!")
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error seeding candidates: {e}")
            raise
        finally:
            self.session.close()

    def clear(self):
        """Clear all seeded candidates"""
        try:
            count = self.session.query(Candidate).count()
            self.session.query(Candidate).delete()
            self.session.commit()
            print(f"🗑️  Cleared {count} candidates from the database")
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error clearing candidates: {e}")
            raise
        finally:
            self.session.close()


def seed_candidates():
    """Main function to seed candidates"""
    seeder = CandidateSeeder()
    seeder.seed()


def clear_candidates():
    """Main function to clear candidates"""
    seeder = CandidateSeeder()
    seeder.clear()


if __name__ == "__main__":
    seed_candidates()
