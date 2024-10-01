# PoultryTrack

PoultryTrack is a comprehensive poultry management system designed to streamline the operations of hatcheries, breeders, inventory, and human resources. The project also includes interactive analytics and dashboard functionalities to provide real-time insights and manage chicks and egg tracking processes.

## Features

### 1. **Breeders and Breed Management**

- Add, update, and manage breeders and their associated breeds.
- Track the number of hens, cocks, mortality, and other relevant breeder data.
- Easily upload and manage photos of breeders.

### 2. **Hatchery Management**

- Handle hatchery processes such as egg setting, candling, incubation, and hatching.
- Record and manage egg batches with detailed hatchery information.
- Monitor hatchery progress and performance throughout the incubation cycle.

### 3. **Chick and Egg Tracker Management**

- Track chicks and eggs using unique codes for detailed lifecycle monitoring.
- Manage separate tracker codes and barcodes for each egg or chick for easy identification.
- Generate reports and view tracker details in PDF format.

### 4. **Inventory Management**

- Keep track of stock levels, poultry feed, equipment, and other assets.
- Manage incoming and outgoing inventory for seamless hatchery and poultry operations.

### 5. **Poultry Management**

- Track the current number of birds, including hens, cocks, butchered, and sold birds.
- Calculate mortality rates and adjust poultry counts accordingly.

### 6. **Human Resource Management**

- Manage staff details, attendance, and roles within the hatchery and poultry farms.

### 7. **Interactive Analytics and Dashboard**

- Visualize data related to hatcheries, breeders, inventory, and human resources.
- Interactive charts and graphs provide actionable insights for decision-making.

## Docker Configuration

PoultryTrack is fully containerized using Docker to simplify setup, configuration, and deployment. Docker ensures that the application can run consistently across multiple environments.

### Environment Variables

The application relies on certain environment variables for configuration, especially for email and database settings. Here’s a list of environment variables to be set up:

#### Email Configuration

```env
EMAIL_USE_TLS=True  # Set to True to use TLS
EMAIL_HOST=smtp.gmail.com  # Email service provider
EMAIL_PORT=587  # Port for TLS
EMAIL_HOST_USER=your_email@example.com  # Your email address
EMAIL_HOST_PASSWORD=your_email_password  # Your email password or app-specific password
```

#### PostgreSQL Database Configuration

```env
POSTGRES_DB=your_database_name  # Name of your PostgreSQL database
POSTGRES_USER=your_database_user  # PostgreSQL username
POSTGRES_PASSWORD=your_database_password  # PostgreSQL password
```

#### General Database Configuration

```env
DB_NAME=your_database_name  # Name of your database
DB_HOST=db
DB_PASSWORD=your_database_password  # Database password
DB_PORT=5432  # Default PostgreSQL port
DB_USER=your_database_user  # Database username
BASE_URL=http://localhost:11000
```

### Setup

To get started with PoultryTrack, follow these instructions:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/EsubalewAmenu/Blockchain-Based-Poultry-Management.git
   cd Blockchain-Based-Poultry-Management
   ```
2. **Create `.env` file**Set up your environment variables by creating a `.env` file in the project root and include the configurations mentioned above.
3. **Build the Docker images:**

   ```bash
   docker-compose build
   ```
4. **Run the application:**

   ```bash
    docker-compose up -d
   ```
5. **Stop the application**

   ```
   docker compose down
   ```
6. **Create the administrator user**

   ```
   docker compose exec -it app bash

   and run the folloeing command 

   python manage.py create_user --email MYOUR EMAIL HERE> --first_name <YOUR FIRST NAME> --last_name <YOUR LAST NAME> --primary_phone +251900123456 --role Administrator -
   -department Admin --is_superuser

   then check your email for credentials
   ```
7. **Access the application:**
   The application will be accessible at `http://localhost:11000`.

## Requirements

- Docker
- Docker Compose
