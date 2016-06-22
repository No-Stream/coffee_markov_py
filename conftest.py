import pytest

@pytest.fixture(scope="session", autouse=True)
def init_():
    """logging.basicConfig(level=logging.CRITICAL)
    logger = logging.getLogger(__name__)"""
    print("Initialized testing session.")
