from app.views import TabsView
from user.mixins import IsVolunteerMixin
git
class Scanner(IsVolunteerMixin, TabsView):
    template_name = 'scanning/scanner.html'

    def get_current_tabs(self):
        return []
