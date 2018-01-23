from django.core.exceptions import ObjectDoesNotExist


class Relationship:

    def __init__(self, primary, secondary, *, related_name=None, many=None):
        self.many, self.related_name = many, related_name
        self.primary, self.secondary = primary, secondary

    def make(self, *, related_name=None, many=None):
        self._fill_attributes(many=many, related_name=related_name)
        self._check_all_attributes_filled()
        self._check_relatedname()

        if self.has_relationship():
            return

        is_ok = True
        if self.many:
            related_manager = getattr(self.primary, self.related_name)
            try:
                related_manager.add(self.secondary)
            except TypeError:
                is_ok = False
        else:
            try:
                setattr(self.primary, self.related_name, self.secondary)
            except ValueError:
                is_ok = False

        if not is_ok:
            raise TypeError("Can't create relationship between these classes."
                            " Probably they don't have a relationship or"
                            " tried the wrong related_name.")

    def has_relationship(self):
        self._check_relatedname()
        self._check_all_attributes_filled()

        has_relationship_bool = False
        if hasattr(self.primary, self.related_name):
            if self.many:
                related_manager = getattr(self.primary, self.related_name)
                has_relationship_bool = self.secondary in related_manager.all()
            else:
                related_attribute = getattr(self.primary, self.related_name)
                has_relationship_bool = related_attribute == self.secondary

        return has_relationship_bool

    def _check_relatedname(self):
        if not self.related_name:
            raise AttributeError('related_name was not provided.')

        swapped = False
        is_valid = True

        while True:
            try:
                getattr(self.primary, self.related_name)
            except ObjectDoesNotExist:
                break
            except AttributeError:
                self.primary, self.secondary = self.secondary, self.primary

                if swapped:
                    is_valid = False
                    break
                swapped = True
            break

        if not is_valid:
            raise AttributeError('related_name passed is not valid for any'
                                 ' of given objects.')

    def _check_all_attributes_filled(self):
        missing = ''

        if self.many is None:
            missing = 'many'
        elif not self.related_name:
            missing = 'related_name'
        if missing:
            raise AttributeError("Not enough information, '{}' is missing."
                                 .format(missing))

    def _fill_attributes(self, primary=None, secondary=None,
                         many=None, related_name=None):

        self.primary = primary or self.primary
        self.secondary = secondary or self.secondary
        self.related_name = related_name or self.related_name
        self.many = many if many is not None else self.many

    def __str__(self):
        primary_name = self.primary.__class__.__name__
        secondary_name = self.secondary.__class__.__name__

        return "{} has{}{}".format(
            primary_name,
            " many " if self.many else " ",
            secondary_name
        )
