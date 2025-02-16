# Real Estate Microservices Project 🏡🚀

This project is a scalable, microservices-based real estate platform where users can **buy, sell, rent properties, and invest**. The system is built with **FastAPI, GraphQL (Apollo Federation), Next.js, PostgreSQL, Redis, RabbitMQ, and Elasticsearch**, ensuring **high performance and scalability**.

## 🔧 Tech Stack

- **Backend:** FastAPI (Python), GraphQL (Apollo Federation)
- **Frontend:** Next.js (React)
- **Database:** PostgreSQL, Redis (caching), Elasticsearch (search)
- **Messaging Queue:** RabbitMQ (async tasks & notifications)
- **Payments:** Stripe (for PRO subscriptions)
- **AI Models:** Price Prediction & Recommendation Engine
- **Infrastructure:** Docker, Nginx, CI/CD with GitHub Actions

## 📌 Core Features

### 🔐 Authentication & User Management

- User Registration & Login (JWT-based authentication)
- Email verification
- Role-based Access (Admin, Realtor, Agency, User)

### 🏠 Property Management

- Users & Agents can post, update, and delete listings
- Agencies can have multiple agents & manage properties
- Property media uploads (Cloudinary integration)

### 🔍 Advanced Search & Filtering

- **Elasticsearch-powered fuzzy search**
- Filters: Location, Price, Type, Bedrooms, Amenities, etc.

### 📊 Investment & AI Analytics

- **AI Price Prediction** based on historical property data
- **Recommendation System** for personalized suggestions
- **Investment Calculator** (ROI, Mortgage, Profit Estimations)

### 💳 Subscription & Monetization

- **PRO Accounts for Realtors & Agencies (via Stripe)**
- **Premium Features:** Featured Listings, Analytics Dashboard

### 📩 Messaging & Notifications

- **Real-time chat** between buyers & sellers
- **Email & push notifications** for property updates & offers

## 🛠 System Architecture

The system follows a **microservices-based approach** with services communicating via **GraphQL Federation & RabbitMQ**.

### 📌 Key Microservices:

| Service                  | Description                                  |
| ------------------------ | -------------------------------------------- |
| **Auth Service**         | User management, JWT auth, role-based access |
| **User Service**         | Profile management, user preferences         |
| **Property Service**     | CRUD for properties, agent & agency listings |
| **Search Service**       | Elasticsearch-powered search                 |
| **AI Service**           | Price prediction, recommendation engine      |
| **Investment Service**   | ROI & mortgage calculators                   |
| **Subscription Service** | Stripe payments for PRO accounts             |
| **Messaging Service**    | Chat, email & push notifications             |

**🖥 API Gateway** (GraphQL with Apollo Federation) handles communication between all services.

## 🚀 Deployment & DevOps

- **Docker** for containerization
- **Nginx & Load Balancer** for request distribution
- **GitHub Actions CI/CD** for automated builds & deployments

## 🏗 Local Development Setup

### Prerequisites

- **Docker & Docker Compose**
- **Python 3.10+**
- **Node.js 18+ & npm/yarn**

### Steps to Run the Project

1. **Clone the repository**

   ```sh
   git clone https://github.com/your-org/real-estate-platform.git
   cd real-estate-platform
   ```

2. **Set up environment variables** (Copy `.env.example` to `.env` and fill in values)

   ```sh
   cp .env.example .env
   ```

3. **Run services with Docker Compose**

   ```sh
   docker-compose up --build
   ```

4. **Access the services**

   - **Frontend:** `http://localhost:3000`
   - **GraphQL Gateway:** `http://localhost:4000/graphql`
   - **API Services:** `http://localhost:8000/docs` (example for FastAPI docs)

## 🎯 Contribution Guide

1. **Fork the repo & create a new branch**
   ```sh
   git checkout -b feature/new-feature
   ```
2. **Commit your changes**
   ```sh
   git commit -m "Add new feature"
   ```
3. **Push and open a PR**
   ```sh
   git push origin feature/new-feature
   ```

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Happy coding! 🚀

