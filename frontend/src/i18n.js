export const dict = {
  ru: {
    login: 'Вход',
    email: 'Электронная почта',
    password: 'Пароль',
    enter: 'Войти',
    register: 'Регистрация',
    first_name: 'Имя',
    last_name: 'Фамилия',
    role: 'Роль',
    employee: 'Сотрудник',
    manager: 'Менеджер',
    logout: 'Выход',
    my_tasks: 'Мои задачи',
    create_task: 'Создать задачу',
    pending: 'Ожидание',
    incorrect: 'В работе',
    done: 'Завершена',
    status: 'Статус',
    progress: 'Прогресс',
    update_task: 'Обновить задачу',
    comments: 'Комментарии',
    no_comments: 'Комментариев пока нет',
    add_comment: 'Добавить комментарий',
    post: 'Отправить',
  }
};

export const currentLang = 'ru';
export const t = (k) => dict[currentLang][k] ?? k; 