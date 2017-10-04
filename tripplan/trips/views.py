import datetime

from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, ListView, \
    CreateView, DeleteView, DetailView
from django.utils import timezone
from django.contrib.auth import authenticate

from .models import Trip, TripLocation

from account_info.models import User

from .forms import CreateTripForm


class LoginRequiredMixin:
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            return super(LoginRequiredMixin, self).get(self, request, *args, **kwargs)
        else:
            redirect_path = reverse('authentication:signin')
            redirect_next = '?next=' + request.path
            return redirect(redirect_path + redirect_next)

    def post(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            return super(LoginRequiredMixin, self).post(self, request, *args, **kwargs)
        else:
            redirect_path = reverse('authentication:signin')
            redirect_next = '?next=' + request.path
            return redirect(redirect_path + redirect_next)

class TripList(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/index.html'

    def get_context_data(self, **kwargs):
        context = super(TripList, self).get_context_data(**kwargs)
        context['upcoming_trip_list'] = Trip.objects.filter(
            start_date__gte=timezone.now()).order_by('start_date')
        context['past_trip_list'] = Trip.objects.filter(
            start_date__lt=timezone.now()).order_by('start_date')
        return context

class TripView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'trips/detail.html'

    def get_context_data(self, **kwargs):
        context = super(TripView, self).get_context_data(**kwargs)
        trip = self.get_object()

        # Context for page title
        context['page_title'] = trip.title
        if trip.number_nights > 0:
            context['end_date'] = trip.start_date + datetime.timedelta(days=trip.number_nights)

        # Context for trailhead / endpoint section
        context['trailhead'] = trip.get_trailhead()
        context['endpoint'] = trip.get_endpoint()

        # Context for objective setion
        context['objectives'] = trip.get_location_context(TripLocation.OBJECTIVE)
        # import pdb; pdb.set_trace()

        # Context for camp location section
        context['camp_locations'] = trip.get_location_context(TripLocation.CAMP)

        return context

# class TripEditView(LoginRequiredMixin, UpdateView):
#     model = Trip
#     template_name = 'trips/edit.html'
#     form_class = TripLocationForm
#
#     def get_context_data(self, **kwargs):
#         context = super(TripEditView, self).get_context_data(**kwargs)
#         trip = self.get_object()
#         context['page_title'] = trip.title
#         context['save_button_title'] = 'Save Trip'
#         context['cancel_button_path'] = 'trips:trip_list'
#         if trip.number_nights > 0:
#             context['end_date'] = trip.start_date + datetime.timedelta(days=trip.number_nights)
#         return context

class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    template_name = 'trips/create.html'
    form_class = CreateTripForm

    def get_context_data(self, **kwargs):
        context = super(TripCreateView, self).get_context_data(**kwargs)
        context['page_title'] = 'Start a new trip'
        context['save_button_title'] = 'Save Trip'
        context['cancel_button_path'] = 'trips:trip_list'
        return context

    def get_success_url(self):
        return reverse('trips:trip_detail', args=(self.object.id,))


# # class UserView(generic.DetailView):
# #     model = User
# #     template_name = 'users/detail.html'
# #
# #     def get_context_data(self, **kwargs):
# #         context = super(UserView, self).get_context_data(**kwargs)
# #         context['vehicle_list'] = self.object.vehicle_set.all()
# #         return context
#
# class VehicleView(generic.DetailView):
#     model = Vehicle
#     template_name = 'vehicles/detail.html'
#
# class VehicleCreateView(generic.CreateView):
#     model = Vehicle
#     template_name = 'vehicles/create.html'
#     fields = ['year', 'make', 'model', 'lic_plate_num',
#               'lic_plate_st']
#
#     # def get_success_url(self, **kwargs):
#     #     return reverse('trips:user_detail', args=(self.kwargs['user_id'],))
#
#     def get_context_data(self, **kwargs):
#         context = super(VehicleCreateView, self).get_context_data(**kwargs)
#         context['user'] = User.objects.get(pk=self.kwargs['user_id'])
#         return context
#
#     def form_valid(self, form):
#         form.instance.user = User.objects.get(pk=self.kwargs['user_id'])
#         return super(VehicleCreateView, self).form_valid(form)

def notifications(request):
    return render(request, 'trips/notifications.html')
