from django.shortcuts import render


def trigger_error(request):
    _division_by_zero = 1 / 0
