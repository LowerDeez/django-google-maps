from django.db.models import Avg, FloatField, ExpressionWrapper, Func
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, ListView, UpdateView

from cities.forms import CityCreateForm, CityDetailForm
from cities.models import City


class CityListView(ListView):
    queryset = City.objects.all()
    template_name = "cities/list.html"
    context_object_name = "cities"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avg_lat'] = City.objects.all().annotate(
            lat=ExpressionWrapper(
                Func(
                    'coordinates',
                    function='ST_Y'
                ),
                output_field=FloatField()
            )
        ).annotate(
            long=ExpressionWrapper(
                Func(
                    'coordinates',
                    function='ST_X'
                ),
                output_field=FloatField()
            )
        ).order_by('lat')

        context['avg_long'] = City.objects.all().annotate(
            long=ExpressionWrapper(
                Func(
                    'coordinates',
                    function='ST_X'
                ),
                output_field=FloatField()
            )
        ).order_by('long')

        print([(obj.lat, obj.long) for obj in context['avg_lat']])
        context['center'] = context['avg_lat'].aggregate(avg_long=Avg('long'), avg_lat=Avg('lat'))
        return context


class CityDetailView(UpdateView):
    form_class = CityDetailForm
    model = City
    template_name = "cities/detail.html"


class CityCreateView(FormView):
    template_name = "cities/form.html"
    form_class = CityCreateForm
    success_url = reverse_lazy("cities:list")

    def form_valid(self, form):
        form.save()
        return super(CityCreateView, self).form_valid(form)