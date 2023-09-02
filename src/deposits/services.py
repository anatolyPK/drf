from deposits.models import PersonsDeposits


def add_or_take_sum_from_deposit(transaction):
    deposit = PersonsDeposits.objects.filter(id=transaction.deposit_id).first()
    deposit.deposits_summ += transaction.size if transaction.is_add_or_take else -transaction.size
    deposit.save()

