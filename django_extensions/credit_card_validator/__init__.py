from .validators import CreditCardValidator, validate_credit_card, get_card_type, is_valid_credit_card

is_valid_card = is_valid_credit_card  # Alias

__all__ = ['CreditCardValidator', 'validate_credit_card', 'get_card_type', 'is_valid_credit_card', 'is_valid_card']
