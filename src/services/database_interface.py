from crypto.models import PersonsCrypto, PersonsTransactions
from stocks.models import UserStock, UserTransaction

import abc
from typing import Hashable, Callable, Literal


class AbstractBD(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_data(cls, model, queryset_method, **kwargs):
        return cls.__queryset_methods[queryset_method](model, **kwargs)

    @staticmethod
    @abc.abstractmethod
    def put_data(model, id, **kwargs):
        model_object, created = model.objects.update_or_create(id=id, defaults=kwargs)
        return model_object, created

    @staticmethod
    def __get_all_objects(model, **kwargs):
        return model.objects.all()

    @staticmethod
    def __get_one_object(model, **kwargs):
        return model.objects.get(**kwargs)

    @staticmethod
    def __get_filter_objects(model, **kwargs):
        return model.objects.filter(**kwargs)

    __queryset_methods = {
        'all': __get_all_objects,
        'get': __get_one_object,
        'filter': __get_filter_objects
    }


class CryptoBd(AbstractBD):
    model = PersonsCrypto
    transaction_model = PersonsTransactions

    @classmethod
    @abc.abstractmethod
    def get_data(cls, is_transaction, queryset_method, **kwargs):
        return super().get_data(model=cls.__get_model(is_transaction),
                                queryset_method=queryset_method,
                                **kwargs)

    @classmethod
    @abc.abstractmethod
    def put_data(cls, id, is_transaction, **kwargs):
        return super().put_data(model=cls.__get_model(is_transaction),
                                id=id,
                                **kwargs)

    @classmethod
    def __get_model(cls, is_transaction):
        return cls.transaction_model if is_transaction else cls.model


class StockBd(AbstractBD):
    model = UserStock
    transaction_model = UserTransaction

    @classmethod
    @abc.abstractmethod
    def get_data(cls, is_transaction, queryset_method, **kwargs):
        return super().get_data(model=cls.__get_model(is_transaction),
                                queryset_method=queryset_method,
                                **kwargs)

    @classmethod
    @abc.abstractmethod
    def put_data(cls, id, is_transaction, **kwargs):
        return super().put_data(model=cls.__get_model(is_transaction),
                                id=id,
                                **kwargs)

    @classmethod
    def __get_model(cls, is_transaction):
        return cls.transaction_model if is_transaction else cls.model


class ClassNotFoundError(ValueError):
    pass


class Factory(object):
    """Фабрика, возвращающая нужный класс типа актива"""
    @staticmethod
    def get(assets_type: Hashable) -> object:
        """Возвращает нужный класс переданного типа актива"""
        if not isinstance(assets_type, Hashable):
            raise ValueError("class_name must be a Hashable type!")
        classes: dict[Hashable, Callable[..., object]] = {
            "crypto": CryptoBd,
            "stock": StockBd
        }
        class_ = classes.get(assets_type, None)
        if class_ is not None:
            return class_
        raise ClassNotFoundError


class DbInterface:
    """Класс для взаимодействия клиента с БД"""

    @staticmethod
    def get_data_from_db(assets_type: Literal['crypto', 'stock'],
                         is_transaction: bool,
                         queryset_method: Literal['all', 'get', 'filter'],
                         **kwargs):
        """Возвращает данные из БД по указанным параметрам.
        В kwargs передавать запрос. Например:
        user=user, figi=figi, token=token_1 и т.д"""
        db_class = Factory.get(assets_type)
        return db_class.get_data(is_transaction=is_transaction,
                                 queryset_method=queryset_method,
                                 **kwargs)

    @staticmethod
    def put_data_to_db(assets_type: Literal['crypto', 'stock'],
                       id: int = None,
                       is_transaction: bool = False,
                       **kwargs):
        """Использует метод .update_or_create, который принимает id(pk) и **kwargs """
        db_class = Factory.get(assets_type)
        return db_class.put_data(is_transaction=is_transaction,
                                 id=id,
                                 **kwargs)


print(DbInterface.get_data_from_db(assets_type='crypto',
                                   is_transaction=False,
                                   queryset_method='all',
                                   ))
print(DbInterface.get_data_from_db(assets_type='stock',
                                   is_transaction=False,
                                   queryset_method='filter',
                                   figi='BBG013J0LT31'))
print(DbInterface.put_data_to_db(assets_type='crypto',
                                 is_transaction=False,

                                 token='usd',
                                 lot=9,
                                 average_price=555
                                 ))
