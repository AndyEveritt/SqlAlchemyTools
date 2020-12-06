from sqlalchemy.orm import Query
from sqlalchemy_tools.pagination import Paginator


class BaseQuery(Query):

    def get_or_error(self, uid, error):
        """Like :meth:`get` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.get(uid)
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def first_or_error(self, error):
        """Like :meth:`first` but raises an error if not found instead of
        returning `None`.
        """
        rv = self.first()
        if rv is None:
            if isinstance(error, Exception):
                raise error
            return error()
        return rv

    def paginate(self, **kwargs):
        """Paginate this results.
        Returns an :class:`Paginator` object.
        - param query: Iterable to paginate. Can be a query object, list or any iterables
        - param page: current page
        - param per_page: max number of items per page
        - param total: Max number of items. If not provided, it will use the query to count
        - param padding: Number of elements of the next page to show
        - param callback: a function to callback on each item being iterated.
        - param static_query: bool - When True it will return the query as is , without slicing/limit. Usally when using the paginator to just create the pagination.
        # To customize the pagination
        - param left_edge:
        - param left_current:
        - param right_current:
        - param right_edge:
        """
        return Paginator(self, **kwargs)
