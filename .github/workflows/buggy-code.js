// Buggy code for testing AI PR reviewer

function getUserData(userId) {
  // Bug 1: No null check
  const user = users.find(u => u.id === userId);
  return user.name;  // Will crash if user not found
}

async function fetchAndProcess(url) {
  // Bug 2: No error handling on network call
  const response = await fetch(url);
  const data = await response.json();
  
  // Bug 3: Will crash if data.items is undefined
  return data.items.map(item => item.value);
}

function divide(a, b) {
  // Bug 4: No division by zero check
  return a / b;
}

function processArray(arr) {
  // Bug 5: No check if arr is actually an array
  let total = 0;
  for (let i = 0; i <= arr.length; i++) {  // Bug 6: <= causes out-of-bounds
    total += arr[i];
  }
  return total;
}

// Bug 7: Hardcoded API key (security issue)
const API_KEY = "sk-1234567890abcdef";

// Bug 8: console.log in production code
console.log("This should not be in production");

// Bug 9: Missing error handling
const result = JSON.parse(userInput);  // Will crash on invalid JSON

// Bug 10: Memory leak - no cleanup
setInterval(() => {
  console.log("Running forever");
}, 1000);

module.exports = {
  getUserData,
  fetchAndProcess,
  divide,
  processArray,
};
