# KidGPT

KidGPT is a Flask-based web application that provides a child-friendly interface for interacting with AI. The application is designed to be safe, educational, and engaging for young users while maintaining appropriate content filtering and supervision capabilities. Currently only works with the OpenAI API.

## ⚠️ Important Security Notice

This application is designed for local network use only and should NOT be exposed to the internet. It lacks certain security features (like CSRF protection) that would be necessary for internet-facing deployment. Always run this application behind a firewall and only on trusted local networks.

## 🚀 Features

- Child-friendly AI interaction interface
- Ability for parents to create 'personas' with custom system instructions
- Ability for parents to set custom system instructions for each child
- Each user's conversation history is maintained
- Built with Flask and OpenAI integration
- Basic user authentication
- MySQL database for data persistence
- Docker support for easy deployment

## 👤 User Types

KidGPT features three different user roles:

- **Admin Parent**: A parent account with access to change the technical details of the KidGPT instance, such as the OpenAI key. Has all the rights of a User Parent as well.
- **User Parent**: A parent account with access to change settings for their kids, such as adding new banned words, customizing their childrens' system instructions, and creating personas.
- **Child**: A child account that only has access to chat with the bot. Cannot configure any instance settings.

## 🏁 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/KidGPT.git
   cd KidGPT
   ```

2. **Create a `.env` file in the project root with the following variables:**
   ```env
   MYSQL_ROOT_PASSWORD=your_mysql_root_password
   FERNET_KEY=your_fernet_key
   FLASK_SECRET_KEY=your_flask_secret_key
   ```
   - You can generate a Fernet key with:
     ```python
     python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
     ```

3. **Start the app using Docker Compose:**
   ```bash
   docker-compose up --build
   ```
   This will start both the MySQL database and the KidGPT Flask app. The app will be available at [http://localhost](http://localhost).

4. **Database Initialization:**
   - The database will be automatically initialized using the scripts in `initdb/` on first run.

## Using the App

- Open your browser and go to [http://localhost](http://localhost).
- On first access you will be prompted to set up an account. The user you create will be created with the Admin Parent role.
- As your admin user, navigate to the Admin settings page and create any other accounts you would like. See the role descriptions to make sure you set the roles up correctly.

## ⚙️ Environment Variables

The following environment variables are required (set in your `.env` file):
- `MYSQL_ROOT_PASSWORD`: Password for the MySQL root user.
- `FERNET_KEY`: Key for encrypting sensitive data (generate with the command above).
- `FLASK_SECRET_KEY`: Secret key for Flask session security.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

- To set up a local development environment for testing:
  1. Install the test requirements:
     ```bash
     pip install -r requirements.test.txt
     ```
  2. Run tests with:
     ```bash
     pytest
     ```

- Please ensure your code passes all tests before submitting a PR.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Note

Always supervise children while using AI tools and ensure appropriate content filtering is in place. 