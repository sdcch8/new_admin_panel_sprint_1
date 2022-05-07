import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = '"content"."genre"'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE,
                                  verbose_name=_('film_work'))
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE,
                              verbose_name=_('genre'))
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = '"content"."genre_film_work"'
        verbose_name = _('GenreFilmwork')
        verbose_name_plural = _('GenreFilmworks')

    def __str__(self):
        return '{film_work} / {genre}'.format(film_work=self.film_work.title,
                                              genre=self.genre.name)


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'), max_length=255)

    class Meta:
        db_table = '"content"."person"'
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE,
                                  verbose_name=_('film_work'))
    person = models.ForeignKey('Person', on_delete=models.CASCADE,
                               verbose_name=_('person'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    role = models.TextField(_('role'), null=True)

    class Meta:
        db_table = '"content"."person_film_work"'
        verbose_name = _('PersonFilmwork')
        verbose_name_plural = _('PersonFilmworks')

    def __str__(self):
        return '{title} / {name} / {role}'.format(title=self.film_work.title,
                                                  name=self.person.full_name,
                                                  role=self.role)


class Filmwork(UUIDMixin, TimeStampedMixin):

    class TypeChoices(models.TextChoices):
        MOVIE = _('movie')
        TV_SHOW = _('tv_show')

    title = models.TextField(_('title'))
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'))
    type = models.CharField(_('type'), max_length=255,
                            choices=TypeChoices.choices)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])

    class Meta:
        db_table = '"content"."film_work"'
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworks')

    def __str__(self):
        return self.title
