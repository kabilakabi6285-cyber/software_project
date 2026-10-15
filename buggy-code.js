function getUserData(userId) {
  const user = users.find(u => u.id === userId);
  return user.name;
}

function calculateTotal(items) {
  let total = 0;
  for (let i = 0; i <= items.length; i++) {
    total += items[i].price;
  }
  return total;
}

const API_KEY = "sk-1234567890abcdef";

console.log("Debugging user data");

function divide(a, b) {
  return a / b;
}
