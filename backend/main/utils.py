from .serializer import *
from datetime import date, datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import os
import uuid
from django.conf import settings


def is_admin_user(user):
    admin_roles = ['MasterAdmin', 'SPbUAdmin', 'POMIAdmin']

    user_roles = user.roles.all().select_related('role')
    user_role_names = [user_role.role.name for user_role in user_roles]

    return any(role in admin_roles for role in user_role_names)


def is_master_admin(user):
    return user.roles.filter(role__name='MasterAdmin').exists()


def is_group_admin(user, group):
    if group == 'SPbU':
        return user.roles.filter(role__name='SPbUAdmin').exists()
    elif group == 'POMI':
        return user.roles.filter(role__name='POMIAdmin').exists()
    return False


def validate_post_data(post_type, data):
    errors = {}

    if post_type == 'publication':
        required_fields = ['title', 'language', 'preprint_date', 'preprint_number', 'current_status']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f'Поле {field} обязательно для публикации'

        date_fields = ['preprint_date', 'submission_date', 'acceptance_date', 'publication_date']
        for field in date_fields:
            if data.get(field):
                try:
                    from datetime import datetime
                    datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    errors[field] = f'Неверный формат даты для поля {field}'

    elif post_type == 'presentation':
        details = data.get('details', {})

        required_fields = ['title', 'language', 'presentation_place', 'presentation_date']
        for field in required_fields:
            if not details.get(field):
                errors[field] = f'Поле {field} обязательно для доклада'

        if details.get('presentation_date'):
            try:
                from datetime import datetime
                datetime.fromisoformat(details['presentation_date'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                errors['presentation_date'] = 'Неверный формат даты'

    return errors


def is_user_has_access_to_post(user, post):
    return post.authors.filter(user=user).exists() or is_admin_user(user)


def update_post_details(post, details_data):
    from .serializer import PublicationCreateSerializer, PresentationCreateSerializer
    errors = {}

    try:
        if post.type == 'publication' and hasattr(post, 'publication'):
            publication = post.publication

            external_authors = details_data.pop('external_authors_list', None)

            publication_serializer = PublicationCreateSerializer(
                publication,
                data=details_data,
                partial=True
            )

            if publication_serializer.is_valid():
                publication_serializer.save()

                if external_authors is not None:
                    publication.external_authors.all().delete()
                    for author_name in external_authors:
                        if author_name.strip():
                            ExternalPublicationAuthor.objects.create(
                                publication=publication,
                                author_name=author_name.strip()
                            )
            else:
                errors.update(publication_serializer.errors)

        elif post.type == 'presentation' and hasattr(post, 'presentation'):
            presentation = post.presentation
            presentation_serializer = PresentationCreateSerializer(
                presentation,
                data=details_data,
                partial=True
            )

            if not presentation_serializer.is_valid():
                errors.update(presentation_serializer.errors)
            else:
                presentation_serializer.save()

        else:
            errors['type'] = f'Неподдерживаемый тип поста для обновления: {post.type}'

    except Exception as e:
        errors['general'] = str(e)

    return errors


def have_enough_rights(current_user, target_user):

    if current_user.id == target_user.id:
        return True

    if is_master_admin(current_user):
        return True
    print(7777)
    current_user_groups = get_user_admin_groups(current_user)
    target_user_group = target_user.group
    print(8888)

    if target_user_group in current_user_groups:
        return True

    return False

def can_user_delete_user(current_user, target_user):
    if is_master_admin(current_user):
        return True, ""

    if not is_admin_user(current_user):
        return False, "Доступ запрещен. Требуются права администратора."

    if is_admin_user(target_user):
        return False, "Администратор не может удалить другого администратора."

    current_user_groups = get_user_admin_groups(current_user)
    target_user_group = target_user.group

    if target_user_group not in current_user_groups:
        return False, f"Вы не можете удалить пользователя из группы {target_user_group}"

    return True, ""


def get_user_admin_groups(user):
    groups = []

    if UserRole.objects.filter(user=user, role__name='MasterAdmin').exists():
        groups.extend(['SPbU', 'POMI'])
    if UserRole.objects.filter(user=user, role__name='SPbUAdmin').exists():
        groups.append('SPbU')
    if UserRole.objects.filter(user=user, role__name='POMIAdmin').exists():
        groups.append('POMI')

    return groups

def get_post_details(post):
    if post.type == 'publication' and hasattr(post, 'publication'):
        publication = post.publication
        detail_data = {
            'id': publication.id,
            'current_status': publication.current_status,
            'title': publication.title,
            'language': publication.language,
            'preprint_date': publication.preprint_date,
            'preprint_number': publication.preprint_number,
            'submission_date': publication.submission_date,
            'journal_name': publication.journal_name,
            'journal_issn': publication.journal_issn,
            'acceptance_date': publication.acceptance_date,
            'doi': publication.doi,
            'publication_date': publication.publication_date,
            'journal_volume': publication.journal_volume,
            'journal_number': publication.journal_number,
            'journal_pages_or_article_number': publication.journal_pages_or_article_number,
            'journal_level': publication.journal_level,
            'files': {
                'preprint': get_file_info(publication.preprint_document_file_path),
                'online_first': get_file_info(publication.submission_document_file_path),
                'published': get_file_info(publication.publicated_document_file_path)
            }
        }

        external_authors = [author.author_name for author in publication.external_authors.all()]
        detail_data['external_authors_list'] = external_authors

        internal_authors = [author.user.id for author in post.authors.all()]
        detail_data['internal_authors_list'] = internal_authors

        return detail_data

    elif post.type == 'presentation' and hasattr(post, 'presentation'):
        presentation = post.presentation
        return {
            'id': presentation.id,
            'title': presentation.title,
            'language': presentation.language,
            'description': presentation.description,
            'presentation_place': presentation.presentation_place,
            'presentation_date': presentation.presentation_date,
            'files': {}
        }

    return {}

def get_file_info(file_path):
    if file_path and file_path.strip():
        import os
        file_name = os.path.basename(file_path)
        return {
            'exists': True,
            'file_name': file_name
        }
    else:
        return {
            'exists': False,
            'file_name': ''
        }

def quarter_to_dates(quarter: int, year: int):
    if quarter == 1:
        return date(year, 1, 1), date(year, 3, 31)
    if quarter == 2:
        return date(year, 4, 1), date(year, 6, 30)
    if quarter == 3:
        return date(year, 7, 1), date(year, 9, 30)
    if quarter == 4:
        return date(year, 10, 1), date(year, 12, 31)
    raise ValueError("quarter must be from 1 to 4")


def get_period(data: dict):
    load_type = data.get("load_type")
    if load_type == "quarterly":
        start_q = data["start_quarter"]
        end_q = data["end_quarter"]
        start_quarter = int(start_q["quarter"])
        start_year = int(start_q["year"])
        end_quarter = int(end_q["quarter"])
        end_year = int(end_q["year"])
        start_date, _ = quarter_to_dates(start_quarter, start_year)
        _, end_date = quarter_to_dates(end_quarter, end_year)
    elif load_type == "yearly":
        year = int(data["year"]) 
        start_date, end_date = date(year, 1, 1), date(year, 12, 31)
    else:
        raise ValueError("load_type must be quarterly or yearly")
    return start_date, end_date

def get_publication_status_on_date(publication, target_date):
    if publication.publication_date and publication.publication_date <= target_date:
        return "published"
    elif publication.acceptance_date and publication.acceptance_date <= target_date:
        return "accepted"
    elif publication.submission_date and publication.submission_date <= target_date:
        return "submitted"
    elif publication.preprint_date and publication.preprint_date <= target_date:
        return "preprint"
    return None

def format_publication_for_rtf(publication, target_date):
    status = get_publication_status_on_date(publication, target_date)
    if not status:
        return None

    def get_author_initials(user):
        parts = []
        if user.second_name_rus:
            parts.append(user.second_name_rus)
        if user.first_name_rus:
            parts.append(f"{user.first_name_rus[0]}.")
        if user.middle_name_rus:
            parts.append(f"{user.middle_name_rus[0]}.")
        return " ".join(parts) if parts else user.username

    internal_authors = [get_author_initials(p_a.user) for p_a in publication.post.authors.all()]
    
    external_authors = [e_a.author_name for e_a in publication.external_authors.all()]
    
    all_authors = internal_authors + external_authors
    authors_str = ", ".join(all_authors)

    title = publication.title or "Без названия"
    placeholder_file = "[файл]"

    if status == "preprint" and publication.preprint_date:
        year = publication.preprint_date.year
        preprint_number = publication.preprint_number or ""
        return f"{authors_str}. {title} // Препринт - {year} - {preprint_number} - {placeholder_file}"

    elif status == "submitted" and publication.submission_date:
        year = publication.submission_date.year
        journal_name = publication.journal_name or ""
        journal_issn = publication.journal_issn or ""
        return f"{authors_str}. {title} // {journal_name} - {year} - {journal_issn} - {placeholder_file}"

    elif status == "accepted" and publication.acceptance_date:
        year = publication.acceptance_date.year
        journal_name = publication.journal_name or ""
        doi = publication.doi or ""
        return f"{authors_str}. {title} // {journal_name} - {year} - {doi} - {placeholder_file}"

    elif status == "published" and publication.publication_date:
        year = publication.publication_date.year
        journal_name = publication.journal_name or ""
        volume = publication.journal_volume or ""
        number = publication.journal_number or ""
        pages = publication.journal_pages_or_article_number or ""
        return f"{authors_str}: {title} // {journal_name} - {year} - том {volume}, номер {number} - {pages} - {placeholder_file}"

    return None

def collect_user_activity(user, start_date, end_date, include_publications=True, include_presentations=True, only_published=False):
    activity_lines = []

    if include_publications:
        publications = Publication.objects.filter(post__authors__user=user).distinct()
        for pub in publications:
            target_date = end_date
            status = get_publication_status_on_date(pub, target_date)
            if not status:
                continue
            if only_published and status != "published":
                continue

            line = format_publication_for_rtf(pub, target_date)
            if line:
                activity_lines.append(line)

    if include_presentations:
        presentations = Presentation.objects.filter(post__authors__user=user).distinct()
        for pres in presentations:
            pres_date = pres.presentation_date
            if pres_date and start_date <= pres_date <= end_date:
                title = pres.title or "Без названия"
                place = pres.presentation_place or ""
                line = f"{title} // {place} - {pres_date.isoformat()}"
                activity_lines.append(line)

    return activity_lines

def get_target_users(user_type, user_id=None):
    if user_type == "all":
        return User.objects.all()
    elif user_type == "certain":
        return User.objects.filter(id=user_id)
    elif user_type in ["POMI", "SPbU"]:
        return User.objects.filter(group=user_type)
    return User.objects.none()


def can_impersonate_user(admin_user, target_user):
    if not is_admin_user(admin_user):
        return False

    if is_master_admin(admin_user):
        return True

    admin_groups = get_user_admin_groups(admin_user)
    return target_user.group in admin_groups


def create_impersonation_tokens(impersonator, target_user):
    target_refresh = RefreshToken.for_user(target_user)
    target_access = target_refresh.access_token

    target_access['is_impersonating'] = True
    target_access['impersonator_id'] = impersonator.id
    target_access['impersonator_username'] = impersonator.username

    context_refresh = RefreshToken()
    context_refresh['user_id'] = impersonator.id
    context_refresh['target_user_id'] = target_user.id
    context_refresh['is_context_token'] = True
    context_refresh['exp'] = datetime.now() + timedelta(hours=24)

    return {
        'token': str(target_access),
        'context_token': str(context_refresh),
    }


def validate_context_token(context_token):
    try:
        token = RefreshToken(context_token)
        if not token.get('is_context_token', False):
            return None, "Неверный тип токена"

        impersonator_id = token.get('user_id')
        target_user_id = token.get('target_user_id')

        if not impersonator_id or not target_user_id:
            return None, "Неверный формат токена"

        try:
            impersonator = User.objects.get(id=impersonator_id)
            target_user = User.objects.get(id=target_user_id)

            active_session = ImpersonationSession.objects.filter(
                impersonator=impersonator,
                target_user=target_user,
                is_active=True
            ).first()

            if not active_session:
                return None, "Сессия имперсонализации неактивна"

            return {
                'impersonator': impersonator,
                'target_user': target_user,
                'session': active_session
            }, None

        except User.DoesNotExist:
            return None, "Пользователь не найден"

    except Exception as e:
        return None, f"Неверный токен: {str(e)}"


def get_impersonation_status(user, token):
    try:
        access_token = AccessToken(token)
        is_impersonating = access_token.get('is_impersonating', False)

        if is_impersonating:
            impersonator_id = access_token.get('impersonator_id')
            try:
                impersonator = User.objects.get(id=impersonator_id)
                return {
                    'is_impersonating': True,
                    'impersonator': {
                        'id': impersonator.id,
                        'username': impersonator.username,
                        'first_name_rus': impersonator.first_name_rus,
                        'second_name_rus': impersonator.second_name_rus,
                    }
                }
            except User.DoesNotExist:
                return {'is_impersonating': False}

        return {'is_impersonating': False}

    except Exception:
        return {'is_impersonating': False}


def can_user_assign_roles(current_user, roles_to_assign):
    current_user_roles = [ur.role.name for ur in UserRole.objects.filter(user=current_user)]

    if 'MasterAdmin' in current_user_roles:
        return True, ""

    if 'SPbUAdmin' in current_user_roles:
        for role in roles_to_assign:
            if role != 'SPbUUser':
                return False, "SPbUAdmin может назначать только роль SPbUUser"
        return True, ""

    if 'POMIAdmin' in current_user_roles:
        for role in roles_to_assign:
            if role != 'POMIUser':
                return False, "POMIAdmin может назначать только роль POMIUser"
        return True, ""

    return False, "Недостаточно прав для назначения ролей"


def get_publication_file_path(publication, file_type, filename):
    year = datetime.now().year
    user_id = publication.post.authors.first().user.id if publication.post.authors.exists() else 0

    ext = filename.split('.')[-1] if '.' in filename else 'pdf'

    unique_filename = f"{file_type}-{year}-{user_id}-{uuid.uuid4().hex[:8]}.{ext}"

    return os.path.join('publications', str(year), unique_filename)


def get_file_field_by_type(publication, file_type):
    file_mapping = {
        'preprint': 'preprint_document_file_path',
        'online_first': 'submission_document_file_path',
        'published': 'publicated_document_file_path'
    }
    return file_mapping.get(file_type)


def get_file_info_by_type(publication, file_type):
    file_field = get_file_field_by_type(publication, file_type)
    if not file_field:
        return None

    file_path = getattr(publication, file_field, None)
    if not file_path or not file_path.strip():
        return None

    return {
        'path': file_path,
        'name': os.path.basename(file_path),
        'full_path': os.path.join(settings.MEDIA_ROOT, file_path) if settings.MEDIA_ROOT else file_path
    }


def delete_publication_file_util(publication, file_type):
    file_info = get_file_info_by_type(publication, file_type)
    if not file_info:
        return False

    try:
        full_path = file_info['full_path']
        if os.path.exists(full_path):
            os.remove(full_path)

        file_field = get_file_field_by_type(publication, file_type)
        setattr(publication, file_field, '')
        publication.save()

        return True
    except Exception:
        return False