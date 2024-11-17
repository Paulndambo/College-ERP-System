from datetime import datetime, timedelta
import calendar
from django.conf import settings

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


from apps.marketing.models import Campaign, Lead
from apps.schools.models import Programme

CAMPAIGN_TYPE_CHOICES = ["Email", "Social Media", "Webinar", "Event"]


def campaigns(request):
    campaigns = Campaign.objects.all().order_by("-created_on")

    if request.method == "POST":
        search_text = request.POST.get("search_text")
        campaigns = Campaign.objects.filter(Q(name__icontains=search_text))

    paginator = Paginator(campaigns, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "campaign_types": CAMPAIGN_TYPE_CHOICES}
    return render(request, "marketing/campaigns/campaigns.html", context)


def campaign_details(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)

    leads = Lead.objects.filter(campaign=campaign)

    paginator = Paginator(leads, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    leads_count = Lead.objects.filter(campaign=campaign).count()
    context = {
        "campaign": campaign,
        "leads_count": leads_count,
        "leads": leads,
        "page_obj": page_obj,
    }
    return render(request, "marketing/campaigns/campaign_details.html", context)


def campaign_drive(request, slug=None):
    campaign = Campaign.objects.get(slug=slug)
    programmes = Programme.objects.all()

    context = {"campaign": campaign, "programmes": programmes}
    return render(request, "marketing/campaigns/campaign.html", context)


def express_interest(request):
    if request.method == "POST":
        campaign = request.POST.get("campaign_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        programme = request.POST.get("programme")

        campaign = Campaign.objects.get(id=campaign)

        Lead.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            source="Campaign",
            programme_id=programme,
            campaign=campaign,
        )

        return redirect("interest-received")
    return render(request, "marketing/campaigns/campaign.html", context)


def interest_received(request):
    return render(request, "marketing/campaigns/interest_received.html")


def new_campaign(request):
    if request.method == "POST":
        name = request.POST.get("name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        description = request.POST.get("description")
        campaign_type = request.POST.get("campaign_type")
        image = request.FILES.get("image")

        campaign = Campaign.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            description=description,
            campaign_type=campaign_type,
            image=image,
        )
        campaign.campaign_link = (
            f"{settings.BASE_URL}/marketing/campaign-drive/{campaign.slug}"
        )
        campaign.save()
        return redirect("campaigns")
    return render(request, "marketing/campaigns/new_campaign.html")


def edit_campaign(request):
    if request.method == "POST":
        campaign_id = request.POST.get("campaign_id")
        name = request.POST.get("name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        description = request.POST.get("description")
        campaign_type = request.POST.get("campaign_type")
        image = request.FILES.get("image")

        campaign = Campaign.objects.get(id=campaign_id)
        campaign.name = name
        campaign.start_date = start_date
        campaign.end_date = end_date
        campaign.description = description
        campaign.campaign_type = campaign_type
        campaign.image = image
        campaign.save()

        campaign.campaign_link = (
            f"{settings.BASE_URL}/marketing/campaign-drive/{campaign.slug}"
        )
        campaign.save()

        return redirect("campaigns")
    return render(request, "marketing/campaigns/edit_campaign.html")


def delete_campaign(request):
    if request.method == "POST":
        campaign_id = request.POST.get("campaign_id")
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.delete()
        return redirect("campaigns")
    return render(request, "marketing/campaigns/delete_campaign.html")


class CollectCampainsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("******************* This views was reached ************************")
        campaign_id = request.query_params.get("campaign_id")
        campaign = Campaign.objects.filter(id=campaign_id).first()

        if campaign:
            campaign.views += 1
            campaign.save()
        return Response(
            {"message": "View successfully recorded!!"}, status=status.HTTP_200_OK
        )
