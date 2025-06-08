import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from logger import log_info, log_error


def load_secrets_from_vault():
    """
    Load required secrets from Azure Key Vault and inject into os.environ.
    Vault URL must be provided via KEYVAULT_URL environment variable.
    """
    try:
        vault_url = os.getenv("KEYVAULT_URL")
        if not vault_url:
            raise ValueError("KEYVAULT_URL is not set in environment variables.")

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)

        required_secrets = [
            "pghost", "pgdatabase", "pguser", "pgpassword",
            "finnhub", "discordwebhooknews", "discordwatchlist", "discordreview"
        ]


        for secret_name in required_secrets:
            try:
                secret = client.get_secret(secret_name)
                os.environ[secret_name] = secret.value
                log_info(f"Loaded secret: {secret_name}")
            except Exception as e:
                log_error(f"Failed to load secret '{secret_name}'", e)

    except Exception as e:
        log_error("Fatal error while loading secrets from Azure Key Vault.", e)
        raise  # Let the function fail hard if secrets can't load
