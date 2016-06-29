from django.contrib import admin
from webadmin.models import *



class EbusinessMembersAdmin(admin.ModelAdmin):
    list_display = ('username','code')

admin.site.register(ebusiness_members,EbusinessMembersAdmin)

class FlowAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('ip','num')
admin.site.register(flow_analytics,FlowAnalyticsAdmin)