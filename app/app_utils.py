import streamlit as st
import logging
from functools import wraps
from exceptions import (
    OpenAIError,
    BadRequestError,
    RecordNotCreatedError,
    RecordUpdateError,
    DBError,
    BotNotFoundError,
    BotIncompleteError,
)


def switch_page(page_name: str):
    """Switch to a different page in the Streamlit app."""
    # Map page names to their file paths
    page_mapping = {
        "lounge": "pages/1_lounge.py",
        "assistant": "pages/2_assistant.py",
        "lab": "pages/3_lab.py",
        "faq": "pages/4_faq.py",
        "terms": "pages/5_terms.py",
    }

    page_name_lower = page_name.lower().replace("_", " ")

    if page_name_lower in page_mapping:
        st.switch_page(page_mapping[page_name_lower])
    else:
        raise ValueError(f"Could not find page {page_name}. Must be one of {list(page_mapping.keys())}")


def cleanup_session_state(keys):
    """Remove specified keys from session state."""
    if keys is None:
        return
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


def handle_openai_error(e, cleanup_keys=None):
    """Handle OpenAI errors with appropriate user messaging."""
    cleanup_session_state(cleanup_keys)
    if e.error_type == "RateLimitError" and "exceeded your current quota" in str(e):
        st.error(
            f"{e}  \n  \n**Friendly reminder:** If you are using a free-trial OpenAI API key, "
            "this error is caused by the extremely low rate limits associated with the key. "
            "To optimize your chat experience, we recommend upgrading to the pay-as-you-go OpenAI plan. "
            "Please see our FAQ for more information."
        )
    else:
        st.error(f"{e}")


def handle_db_error(e, cleanup_keys=None, user_message=None):
    """Handle database errors with appropriate user messaging."""
    cleanup_session_state(cleanup_keys)
    if user_message:
        st.error(user_message)
    else:
        st.error("Could not save data. Please try again later.")


def handle_session_errors(cleanup_keys=None, on_error_callback=None):
    """
    Decorator that handles common session errors with cleanup.

    Args:
        cleanup_keys: List of session state keys to remove on error
        on_error_callback: Optional callback function to call on error (receives exception)

    Usage:
        @handle_session_errors(cleanup_keys=['session_id', 'bot_info'])
        def my_handler():
            # handler logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OpenAIError as e:
                handle_openai_error(e, cleanup_keys)
                if on_error_callback:
                    on_error_callback(e)
            except (RecordNotCreatedError, RecordUpdateError) as e:
                cleanup_session_state(cleanup_keys)
                st.error("Could not save session data. Please try again later.")
                if on_error_callback:
                    on_error_callback(e)
            except BadRequestError as e:
                cleanup_session_state(cleanup_keys)
                st.error(f"{e}")
                if on_error_callback:
                    on_error_callback(e)
            except DBError as e:
                cleanup_session_state(cleanup_keys)
                logging.error(f"Database error: {e}")
                st.error("Something went wrong. Please try again later.")
                if on_error_callback:
                    on_error_callback(e)
            except Exception as e:
                cleanup_session_state(cleanup_keys)
                logging.exception("Unexpected error in handler")
                st.error("Something went wrong. Please try again later.")
                if on_error_callback:
                    on_error_callback(e)
        return wrapper
    return decorator


def handle_bot_errors(error_container=None):
    """
    Decorator that handles bot-related errors.

    Args:
        error_container: Optional Streamlit container to display errors in

    Usage:
        @handle_bot_errors(error_container=my_container)
        def my_handler():
            # handler logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BotNotFoundError:
                container = error_container or st
                container.error("AI assistant could not be found")
                return False
            except BotIncompleteError:
                container = error_container or st
                container.error("AI assistant could not be selected, as it was not configured properly.")
                return False
            except Exception as e:
                container = error_container or st
                logging.exception("Unexpected error in bot handler")
                container.error("Something went wrong. Please try again later.")
                return False
        return wrapper
    return decorator
