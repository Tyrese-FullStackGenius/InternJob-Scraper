from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.utils import timezone
from django.utils.html import format_html
from django.db import models
from django.db.models import Count
from solo.models import SingletonModel


User = get_user_model()


class Configuration(SingletonModel):
    new_opportunity_emails_job_last_run = models.DateTimeField(
        blank=True, null=True)


class ProgramQuerySet(models.QuerySet):
    @staticmethod
    def get_userprogram_ids_with_does_ask_for_cover_letter(val):
        return (
            UserProgram.objects
            .filter(does_ask_for_cover_letter=val)
            .values('program_id')
            .annotate(cnt=Count('program_id'))
            .filter(cnt__gte=2)
            .values_list('program_id', flat=True)
        )

    def does_ask_for_cover_letter(self, val):
        programs_ids = self.get_userprogram_ids_with_does_ask_for_cover_letter(
            val)
        return self.filter(id__in=programs_ids)

    def does_ask_for_cover_letter_not_enough_data(self):
        programs_ids_true = self.get_userprogram_ids_with_does_ask_for_cover_letter(
            True)
        programs_ids_false = self.get_userprogram_ids_with_does_ask_for_cover_letter(
            False)
        return (
            self
            .exclude(id__in=programs_ids_true)
            .exclude(id__in=programs_ids_false)
        )

    def get_programs_with_applications_open(self, is_application_open: bool):
        if is_application_open is True:
            return (
                self.filter(is_application_open=is_application_open)
                .exclude(deadline__lte=timezone.now())
            )
        else:
            return (
                self.filter(is_application_open=is_application_open)
                .exclude(deadline__gte=timezone.now())
            )


class CompanyChoices(models.TextChoices):
    GOLDMAN_SACHS = 'Goldman Sachs'
    MORGAN_STANLEY = 'Morgan Stanley'
    JP_MORGAN = 'JP Morgan'
    EVERCORE = 'Evercore'
    LAZARD = 'Lazard'
    BANK_OF_AMERICA = 'Bank of America'
    BNP_PARIBAS = 'BNP Paribas'
    SOCIETE_GENERALE = 'Societe Generale'
    ROTHSCHILD = 'Rothschild'
    BARCLAYS = 'Barclays'
    HSBC = 'HSBC'
    CITIBANK = 'CitiBank'
    DEUTSCHE_BANK = 'Deutsche Bank'
    BAIN = 'Bain'
    MCKINSEY = 'McKinsey'
    ACCENTURE = 'Accenture'
    BCG = 'Boston Consulting Group'
    MARSHMCLENNAN = 'Oliver Wyman'


class CompanyCategoryChoices(models.TextChoices):
    BOUTIQUE = "BOUTIQUE", "Boutique"
    BANK = "BANK", "Bank"


class Company(models.Model):
    name = models.CharField(
        max_length=255, choices=CompanyChoices.choices, unique=True)
    category = models.CharField(
        max_length=255, choices=CompanyCategoryChoices.choices)
    created_date = models.DateTimeField(
        verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(
        verbose_name='Updated At', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


class ProgramCategoryChoices(models.TextChoices):
    SUMMER = 'SUMMER', 'Summer'
    OFFCYCLE = 'OFFCYCLE', 'Off-Cycle'
    INSIGHT = 'INSIGHT', 'Spring Week'
    OTHER = 'OTHER', 'Other'


class ApplicationCloseReasonChoices(models.TextChoices):
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'
    OTHER = 'OTHER', 'Other'


class Region(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=255, verbose_name='Country',
                            primary_key=True, null=False, blank=False)
    code = models.CharField(max_length=2, unique=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(
        max_length=255, verbose_name='Country', null=False, blank=False)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'country')


class Program(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    deadline_text = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    program_type = models.CharField(max_length=255, blank=True, null=True)
    program_type_description = models.CharField(
        max_length=255, blank=True, null=True)
    cities = models.JSONField(blank=True, null=True)
    is_application_open = models.BooleanField()
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)
    url = models.URLField(blank=True, null=True, max_length=1000)
    application_url = models.URLField(blank=True, null=True, max_length=1000)
    is_details_scraped = models.BooleanField(default=False)
    category = models.CharField(
        max_length=255, choices=ProgramCategoryChoices.choices, default='OTHER')
    external_id = models.CharField(max_length=255, blank=True, null=True)
    found_in_latest_scrape = models.BooleanField(default=False)
    cities_mapped = models.ManyToManyField(City)
    countries_mapped = models.ManyToManyField(Country)
    extra_data = models.JSONField(blank=True, null=True)
    is_visa_sponsorship_provided = models.BooleanField(blank=True, null=True)

    search_vector_column = SearchVectorField(null=True)

    created_date = models.DateTimeField(
        verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(
        verbose_name='Updated At', auto_now=True)

    objects = ProgramQuerySet.as_manager()

    @admin.display(description='External Link')
    def get_external_link(self):
        return (
            format_html(
                f'<a href="{self.url}" target="_blank">Open External</a>')
            if self.url
            else None
        )

    def __str__(self):
        return f'{self.company} | {self.title}'

    class Meta:
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
        indexes = (GinIndex(fields=["search_vector_column"]),)


class UserProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=True)

    is_application_submitted = models.BooleanField(blank=True, null=True)
    is_application_submitted_datetime = models.DateTimeField(
        blank=True, null=True)

    does_ask_for_cover_letter = models.BooleanField(blank=True, null=True)

    is_online_test_taken = models.BooleanField(blank=True, null=True)
    is_online_test_taken_datetime = models.DateTimeField(blank=True, null=True)

    was_there_no_online_test = models.BooleanField(blank=True, null=True)
    online_test_questions = models.TextField(blank=True, null=True)

    is_pre_recorded_video_interview_taken = models.BooleanField(
        blank=True, null=True)
    is_pre_recorded_video_interview_taken_datetime = models.DateTimeField(
        blank=True, null=True)

    pre_recorded_video_interview_format = models.TextField(
        blank=True, null=True)
    was_there_no_pre_recorded_video_interview_stage = models.BooleanField(
        blank=True, null=True)

    is_personal_interview_taken = models.BooleanField(blank=True, null=True)
    is_personal_interview_taken_datetime = models.DateTimeField(
        blank=True, null=True)

    personal_interview_questions = models.TextField(blank=True, null=True)

    is_application_closed = models.BooleanField(blank=True, null=True)
    is_application_closed_datetime = models.DateTimeField(
        blank=True, null=True)

    application_close_reason = models.CharField(
        max_length=255,
        choices=ApplicationCloseReasonChoices.choices,
        blank=True,
        null=True
    )

    created_date = models.DateTimeField(
        verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(
        verbose_name='Updated At', auto_now=True)

    class Meta:
        verbose_name = 'User Program'
        verbose_name_plural = 'User(s) Programs'
        unique_together = ('user', 'program')


class UserProgramNotes(models.Model):
    userprogram = models.ForeignKey(
        UserProgram, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()

    created_date = models.DateTimeField(
        verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(
        verbose_name='Updated At', auto_now=True)

    class Meta:
        verbose_name = 'User Program Notes'
        verbose_name_plural = 'User(s) Programs Notes'


class UserProgramPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    regions = models.JSONField(default=list)
    company_categories = models.JSONField(default=list)
    program_categories = models.JSONField(default=list)

    created_date = models.DateTimeField(
        verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(
        verbose_name='Updated At', auto_now=True)

    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User(s) Preferences'


class UserEmailNotificationPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    email_notifications_enabled = models.BooleanField(default=True)
    regions = models.JSONField(default=list)
    company_categories = models.JSONField(default=list)
    program_categories = models.JSONField(default=list)
    emails_per_day_count = models.PositiveIntegerField(blank=True, null=True)
    near_deadline_notifications_enabled = models.BooleanField(default=True)

    created_date = models.DateTimeField(
        verbose_name='Created At', auto_now_add=True)
    updated_date = models.DateTimeField(
        verbose_name='Updated At', auto_now=True)

    class Meta:
        verbose_name = 'User Email Preferences'
        verbose_name_plural = 'User(s) Email Preferences'


class HistoricalData(models.Model):
    historical_date = models.DateField(
        verbose_name='Historical Date', unique=True)
    total_programs_count = models.PositiveBigIntegerField(
        null=True, blank=True)
    open_programs_count = models.PositiveBigIntegerField(null=True, blank=True)
