"""hrms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

import core.views
import core.su

urlpatterns = [
    url(r'^$', core.views.indexpage),
    url(r'^leaves', core.views.leavespage),
    url(r'^leave/apply/', core.views.applyleave),
    url(r'^calendar/(\d+)/', core.views.calendarpage),
    url(r'^calendar/', core.views.calendarpage),
    url(r'^account/', core.views.account),
    url(r'^policies/(\w+)/', core.views.policies),
    url(r'^timesheet/', core.views.timesheet),

    url(r'^accounts/login/', core.views.loginpage),
    url(r'^accounts/logout/', core.views.logoutpage),

    url(r'^su/rmleave/(\d+)', core.su.removeleave),
    url(r'^su/leaveaction/(\d+)/(\w+)', core.su.leaveaction),
    url(r'^su/calendar/rm/(\d+)', core.su.rmcalendar),
    url(r'^su/calendar/(\d+)', core.su.calendar),
    url(r'^su/calendar/', core.su.calendar),
    url(r'^su/file/', core.su.filealeave),
    url(r'^su/users/', core.su.users),
    url(r'^su/newuser/', core.su.createuser),
    url(r'^su/user/(\d+)', core.su.edituser),
    url(r'^su/', core.su.superuser),

    url(r'^admin/', admin.site.urls),
]
