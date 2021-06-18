from typing import List, Type

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from plan_ilan.exceptaions import ModelNotFoundError
from plan_ilan.utils.general import name_of


def right_replace(string: str, old: str, new: str, count: int = 1):
    return f'{new}'.join(string.rsplit(f'{old}', maxsplit=count))


def flatten_dict(dd, separator='-', prefix=''):
    return {prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(dd, dict) else {prefix: dd}


class PlanIlanRootView(APIView):
    """
    This page shows all the API endpoints we are currently providing.\n
    Mind that the API endpoints that has a "list" prefix returns paginated results.\n
    Play around and take a look yourselves :)
    """
    permission_classes = [permissions.AllowAny]

    @classmethod
    def as_view(cls, registered_view_sets: List[Type], **initkwargs):
        cls.registered_view_sets = registered_view_sets
        return super().as_view(**initkwargs)

    def get(self, request):
        api_root_data = {}
        for view_set in self.registered_view_sets:
            model_class = view_set.queryset.model
            model_name = model_class._meta.verbose_name.replace(' ', '')
            model_name_plural = model_class._meta.verbose_name_plural
            try:
                sample_object_pk = model_class.objects.first().pk
            except (AttributeError, Exception):
                raise ModelNotFoundError(model_class, "Can't generate api-root view")
            details_url = right_replace(reverse(f'{model_name}-detail', args=[sample_object_pk], request=request),
                                        sample_object_pk, f'<{name_of(type(sample_object_pk))}:pk>')
            api_root_data[model_name_plural] = {
                'list': reverse(f'{model_name}-list', request=request),
                'details': details_url
            }
            for extra_action in view_set.get_extra_actions():
                args = [sample_object_pk] if extra_action.detail else []
                view_name = f'{model_name}-{extra_action.url_path}'
                resolved_url = reverse(view_name, args=args, request=request)
                if extra_action.detail:
                    resolved_url = right_replace(resolved_url, sample_object_pk,
                                                 f'<{name_of(type(sample_object_pk))}:pk>')
                api_root_data[model_name_plural][extra_action.url_name] = resolved_url
        return Response(flatten_dict(api_root_data))
