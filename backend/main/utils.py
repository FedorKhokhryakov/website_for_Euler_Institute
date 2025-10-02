from .serializer import *
from datetime import date, datetime


def is_admin_user(user):
    admin_roles = ['MasterAdmin', 'SPbUAdmin', 'POMIAdmin']
    user_role_names = [role.name for role in user.roles.all()]

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
        details = data.get('details', {})

        required_fields = ['title', 'language', 'preprint_date', 'preprint_number', 'current_status']
        for field in required_fields:
            if not details.get(field):
                errors[field] = f'Поле {field} обязательно для публикации'

        date_fields = ['preprint_date', 'submission_date', 'acceptance_date', 'publication_date']
        for field in date_fields:
            if details.get(field):
                try:
                    from datetime import datetime
                    datetime.fromisoformat(details[field].replace('Z', '+00:00'))
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


def get_post_details(post):
    if post.type == 'publication' and hasattr(post, 'publication'):
        publication = post.publication
        detail_data = PublicationReadSerializer(publication).data
        return detail_data

    elif post.type == 'presentation' and hasattr(post, 'presentation'):
        return PresentationReadSerializer(post.presentation).data

    return {}


def update_post_details(post, details_data):
    from serializer import PublicationCreateSerializer, PresentationCreateSerializer
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

    current_user_groups = get_user_admin_groups(current_user)
    target_user_group = target_user.group

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
    if user.roles.filter(name='MasterAdmin').exists():
        groups.extend(['SPbU', 'POMI'])
    if user.roles.filter(name='SPbUAdmin').exists():
        groups.append('SPbU')
    if user.roles.filter(name='POMIAdmin').exists():
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
            'preprint_document_file_path': publication.preprint_document_file_path,
            'submission_date': publication.submission_date,
            'journal_name': publication.journal_name,
            'journal_issn': publication.journal_issn,
            'submission_document_file_path': publication.submission_document_file_path,
            'acceptance_date': publication.acceptance_date,
            'doi': publication.doi,
            'accepted_document_file_path': publication.accepted_document_file_path,
            'publication_date': publication.publication_date,
            'journal_volume': publication.journal_volume,
            'journal_number': publication.journal_number,
            'journal_pages_or_article_number': publication.journal_pages_or_article_number,
            'journal_level': publication.journal_level,
            'publicated_document_file_path': publication.publicated_document_file_path,
        }

        external_authors = [author.author_name for author in publication.external_authors.all()]
        detail_data['external_authors_list'] = external_authors

        return detail_data

    elif post.type == 'presentation' and hasattr(post, 'presentation'):
        presentation = post.presentation
        return {
            'id': presentation.id,
            'title': presentation.title,
            'language': presentation.language,
            'description': presentation.description,
            'presentation_place': presentation.presentation_place,
            'presentation_date': presentation.presentation_date
        }

    return {}

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
        start_date, _ = quarter_to_dates(start_q["quarter"], start_q["year"])
        _, end_date = quarter_to_dates(end_q["quarter"], end_q["year"])
    elif load_type == "yearly":
        year = data["year"]
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
    """
    Формирует строку публикации для RTF в зависимости от статуса на target_date.
    """
    status = get_publication_status_on_date(publication, target_date)
    if not status:
        return None

    internal_authors = [p_a.user.get_full_name() or p_a.user.username for p_a in publication.post.authors.all()]
    external_authors = [e_a.author_name for e_a in publication.external_authors.all()]
    all_authors = internal_authors + external_authors
    authors_str = ", ".join(all_authors)

    title = publication.title or "Без названия"
    year = publication.year or ""
    placeholder_file = "[файл]"

    if status == "preprint":
        preprint_number = publication.preprint_number or ""
        return f"{authors_str}. {title} // Препринт - {year} - {preprint_number} - {placeholder_file}"

    elif status == "submitted":
        journal_name = publication.journal_name or ""
        journal_issn = publication.journal_issn or ""
        return f"{authors_str}. {title} // {journal_name} - {year} - {journal_issn} - {placeholder_file}"

    elif status == "accepted":
        journal_name = publication.journal_name or ""
        doi = publication.doi or ""
        return f"{authors_str}. {title} // {journal_name} - {year} - {doi} - {placeholder_file}"

    elif status == "published":
        journal_name = publication.journal_name or ""
        volume = publication.journal_volume or ""
        number = publication.journal_number or ""
        pages = publication.journal_pages_or_article_number or ""
        return f"{authors_str}. {title} // {journal_name} - {year} - том {volume}, номер {number} - {pages} - {placeholder_file}"


def collect_user_activity(user, start_date, end_date, include_publications=True, include_presentations=True, only_published=False):
    """
    Собирает активность пользователя за период для выгрузки RTF.
    Возвращает список строк публикаций и презентаций.
    """
    activity_lines = []

    if include_publications:
        publications = Publication.objects.filter(post__authors__user=user).distinct()
        for pub in publications:
            target_date = end_date
            if only_published and pub.current_status != "published":
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