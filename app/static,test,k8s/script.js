const form = document.getElementById('task-form');
const taskInput = document.getElementById('task-input');
const taskList = document.getElementById('task-list');
const taskCount = document.getElementById('task-count');
const message = document.getElementById('message');

let tasks = [
  { id: 1, text: 'Review project brief', done: false },
  { id: 2, text: 'Reply to the team update', done: true }
];

function renderTasks() {
  taskList.innerHTML = '';

  tasks.forEach((task) => {
    const item = document.createElement('li');
    item.className = `task${task.done ? ' done' : ''}`;

    const title = document.createElement('span');
    title.className = 'task-title';
    title.textContent = task.text;

    const actions = document.createElement('div');
    actions.className = 'task-actions';

    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'task-toggle';
    toggleButton.textContent = task.done ? 'Undo' : 'Done';
    toggleButton.setAttribute('aria-label', task.done ? `Mark ${task.text} as not done` : `Mark ${task.text} as done`);
    toggleButton.addEventListener('click', () => toggleTask(task.id));

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'task-delete';
    deleteButton.textContent = 'Delete';
    deleteButton.setAttribute('aria-label', `Delete ${task.text}`);
    deleteButton.addEventListener('click', () => deleteTask(task.id));

    actions.append(toggleButton, deleteButton);
    item.append(title, actions);
    taskList.appendChild(item);
  });

  const completed = tasks.filter((task) => task.done).length;
  const total = tasks.length;
  const percent = total ? Math.round((completed / total) * 100) : 0;

  taskCount.innerHTML = `
    <span class="count-badge">${completed}/${total}</span>
    <span class="count-label">completed</span>
    <span class="count-percent">${percent}%</span>
  `;
}

function addTask(text) {
  const trimmed = text.trim();

  if (!trimmed) {
    message.textContent = 'Please enter a task before adding it.';
    return;
  }

  tasks.unshift({
    id: Date.now() + Math.random(),
    text: trimmed,
    done: false
  });

  message.textContent = 'Task added successfully.';
  renderTasks();
  form.reset();
  taskInput.focus();
}

function toggleTask(id) {
  tasks = tasks.map((task) =>
    task.id === id ? { ...task, done: !task.done } : task
  );

  renderTasks();
}

function deleteTask(id) {
  tasks = tasks.filter((task) => task.id !== id);
  message.textContent = 'Task removed.';
  renderTasks();
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  addTask(taskInput.value);
});

renderTasks();
