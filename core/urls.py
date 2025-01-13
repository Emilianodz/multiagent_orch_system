from django.urls import path
from .views import agent_view, router_view, agent_one_view, agent_two_view, health_check_view


urlpatterns = [
    path('agent/', agent_view, name='agent_view'),
    path('router/', router_view, name='router_view'),
    path('agent-one/', agent_one_view, name='agent_one_view'),
    path('agent-two/', agent_two_view, name='agent_two_view'),
    path('health/', health_check_view, name='health_check'),
]

