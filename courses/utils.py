from django.apps import apps
from django.utils import timezone


def update_course_progress(user, course):
    """
    Recalcula el avance del usuario en el curso según las lecciones completadas.
    Retorna la instancia CourseProgress actualizada.
    """
    LessonProgress = apps.get_model('lessons', 'LessonProgress')
    CourseProgress = apps.get_model('courses', 'CourseProgress')

    total = course.lessons.count()
    completed = LessonProgress.objects.filter(
        user=user,
        lesson__course=course,
        completed=True,
    ).count()

    course_progress, _ = CourseProgress.objects.get_or_create(
        user=user,
        course=course,
        defaults={'total_lessons': total},
    )
    course_progress.total_lessons = total
    course_progress.completed_lessons = completed

    if total > 0 and completed >= total:
        course_progress.status = 'completed'
        if not course_progress.completed_at:
            course_progress.completed_at = timezone.now()
    else:
        course_progress.status = 'in_progress'
        course_progress.completed_at = None

    course_progress.save()
    return course_progress
