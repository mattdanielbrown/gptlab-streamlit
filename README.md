# GPT Lab 

## Description 
GPT Lab is a user-friendly [Streamlit](https://streamlit.io) app that lets users interact with and create their own AI Assistants powered by OpenAI's GPT language model. With GPT Lab, users can chat with pre-built AI Assistants or create their own by specifying a prompt and OpenAI model parameters. Our goal is to make AI accessible and easy to use for everyone, so users can focus on designing their Assistants without worrying about the underlying infrastructure.

GPT Lab is also featured in the [Streamlit App Gallery](https://streamlit.io/gallery) among other impressive Streamlit apps.

For more insight into the development process and lessons learned while building GPT Lab, check out this [blog post](https://blog.streamlit.io/building-gpt-lab-with-streamlit/) on the official Streamlit blog.

This README will cover:
- Code structure
- Data models
- Accessing the app
- Running the app Locally
- Contributions
- License

## Code structure
```
+----------------+     +-------------------+     +-------------------+     +------------+
|                |     |                   |     |                   |     |            |
|  Streamlit App |<--->| util_collections  |<--->| api_util_firebase |<--->|  Firestore |
|                |     | (users, sessions, |     |                   |     |            |
|                |     |  bots)            |     |                   |     |            |
+----------------+     +-------------------+     +-------------------+     +------------+
                             |
                             |
                             v
                     +-----------------+     +------------+
                     |                 |     |            |
                     | api_util_openai |<--->|   OpenAI   |
                     |                 |     |            |
                     +-----------------+     +------------+
```

## Data models
```
Users Collection
   |
   | - id: (Firestore auto-ID)
   | - user_hash: string (one-way hash value of OpenAI API key)
   | - created_date: datetime
   | - last_modified_date: datetime
   | - sessions_started: number
   | - sessions_ended: number
   | - bots_created: number
```

```
User_hash Collection
   |
   | - id = one-way hash value of OpenAI API key
   | - user_hash_type: string (open_ai_key)
   | - created_date: datetime
```

```
Bots Collection
   |
   | - id: (Firestore auto-ID)
   | - name: string
   | - tag_line: string
   | - description: string
   | - session_type: number
   | - creator_user_id: string
   | - created_date: datetime
   | - last_modified_date: datetime
   | - active_initial_prompt_id: string
   | - active_model_config_id: string
   | - active_summary_prompt_id: string
   | - showcased: boolean
   | - is_active: boolean
   |
   v
   |--> Model_configs subcollection
   |     |
   |     | - config: map
   |     |     | - model: string 
   |     |     | - max_tokens: number 
   |     |     | - temperature: number 
   |     |     | - top_p: number 
   |     |     | - frequency_penalty: number 
   |     |     | - presence_penalty: number 
   |     | - created_date: datetime
   |     | - is_active: boolean
   |
   v
   |--> Prompts subcollection
         |
         | - message_type: string
         | - message: string
         | - created_date: datetime
         | - is_active: boolean
         | - sessions_started: number
         | - sessions_ended: number
```

```
Sessions Collection
   |
   | - id: (Firestore auto-ID)
   | - user_id: string
   | - bot_id: string
   | - bot_initial_prompt_msg: string
   |
   | - bot_model_config: map
   |     | - model: string 
   |     | - max_tokens: number 
   |     | - temperature: number 
   |     | - top_p: number 
   |     | - frequency_penalty: number 
   |     | - presence_penalty: number 
   |
   | - bot_session_type: number
   | - bot_summary_prompt_msg: string
   | - created_date: datetime
   | - session_schema_version: number
   | - status: number
   | - message_count: number
   | - messages_str: string (encrypted)
   |
   v
   |--> Messages subcollection
         |
         | - created_date: datetime
         | - message: string (encrypted)
         | - role: string
```

## Accessing the app 
You can access the app on the Streamlit Cloud community at [gptlab.streamlit.app](https://gptlab.streamlit.app/). 

To use the app, you will need an OpenAI API key. Don't have one yet? Create one on [the OpenAI website](https://platform.openai.com/account/api-keys). Once you have your API key, enter it into the app when prompted. 

For optimal chatting experience, we recommend using a pay-as-you-go API key. (Free trial API keys are limited to 3 requests a minute, not enough to chat with assistants.) You will need to enter your billing information [here](https://platform.openai.com/account/billing/overview). You can learn more about OpenAI API rate limits [here](https://platform.openai.com/docs/guides/rate-limits/overview).

## Running the app locally

To run the app locally, you will need to:

### 1. Set up your Google Firestore database

GPT Lab uses four main collections: `users`, `user_hash`, `bots`, and `sessions`.

**Important:** You must manually create the following collections before running the app:

1. Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project (or use an existing one)
2. Navigate to **Firestore Database** and click **Create database**
3. Create the required collections:
   - Click **Start collection** and create a collection named `users`
   - Add at least one document (you can use auto-ID and add any field, e.g., `placeholder: true`)
   - Repeat the process to create a `sessions` collection with at least one document

   **Note:** The `user_hash` and `bots` collections will be created automatically by the app, but `users` and `sessions` must exist beforehand.

### 2. Generate and configure your service account credentials

1. In the Firebase Console, go to **Project Settings** (gear icon) > **Service accounts**
2. Click **Generate new private key** to download a JSON file
3. Convert the JSON to TOML format for Streamlit secrets (see below)

**Converting JSON credentials to TOML:**

Your downloaded JSON file will look something like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

Convert it to TOML format in `.streamlit/secrets.toml`:
```toml
[firestore.db-key]
type = "service_account"
project_id = "your-project-id"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

[util]
global_salt = "your-optional-global-salt-for-encryption"
```

**Important notes for the TOML conversion:**
- Each JSON key becomes a TOML key under the `[firestore.db-key]` section
- String values must be wrapped in double quotes
- The `private_key` value contains literal `\n` characters - keep them as-is in the TOML string

For more details on Streamlit Firestore integration, see the [Streamlit blog tutorial](https://blog.streamlit.io/streamlit-firestore-continued/).

### 3. Clone this repository

```bash
git clone https://github.com/dclin/gptlab-streamlit.git
cd gptlab-streamlit
```

### 4. Set up your local environment

```bash
# Set up a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Run the app
streamlit run app/home.py
```

The app should now be running at `http://localhost:8501`.

## Contributions
Contributions are welcomed. Simply open up an issue and create a pull request. If you are introducing new features, please provide a detailed description of the specific use case you are addressing and set up instructions to test. 

Aside: I am new to open source, work full-time,  and have young kids, please bear with me if I don't get back to you right away. 

## License
This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for more details.

