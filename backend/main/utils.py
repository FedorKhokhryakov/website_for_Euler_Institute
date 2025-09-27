from main.serializer import *


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
    from main.serializer import PublicationCreateSerializer, PresentationCreateSerializer
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