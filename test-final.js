function getUser(id) {
  const user = users.find(u => u.id === id);
  return user.name;
}

const API_KEY = "sk-hardcoded-secret";

function divide(a, b) {
  return a / b;
}
