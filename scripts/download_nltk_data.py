import ssl
import nltk

# ⛔️ macOS fix for SSL verification issue
ssl._create_default_https_context = ssl._create_unverified_context

# ✅ Download required resources
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
