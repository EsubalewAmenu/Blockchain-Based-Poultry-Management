// DOM elements
const DOMstrings = {
  stepsBtnClass: 'multisteps-form__progress-btn',
  stepsBtns: document.querySelectorAll(`.multisteps-form__progress-btn`),
  stepsBar: document.querySelector('.multisteps-form__progress'),
  stepsForm: document.querySelector('.multisteps-form__form'),
  stepFormPanelClass: 'multisteps-form__panel',
  stepFormPanels: document.querySelectorAll('.multisteps-form__panel'),
  stepPrevBtnClass: 'js-btn-prev',
  stepNextBtnClass: 'js-btn-next',
  formFields: '.multisteps-form__input[required]',
  overallErrorMessage: '.overall-error-message'
};

// Utility functions

// Remove class from a set of items
const removeClasses = (elemSet, className) => {
  elemSet.forEach(elem => {
    elem.classList.remove(className);
  });
};

// Return exact parent node of the element
const findParent = (elem, parentClass) => {
  let currentNode = elem;
  while (!currentNode.classList.contains(parentClass)) {
    currentNode = currentNode.parentNode;
  }
  return currentNode;
};

// Get active button step number
const getActiveStep = elem => {
  return Array.from(DOMstrings.stepsBtns).indexOf(elem);
};

// Set all steps before clicked (and clicked too) to active
const setActiveStep = activeStepNum => {
  removeClasses(DOMstrings.stepsBtns, 'js-active');
  DOMstrings.stepsBtns.forEach((elem, index) => {
    if (index <= activeStepNum) {
      elem.classList.add('js-active');
    }
  });
};

// Get active panel
const getActivePanel = () => {
  let activePanel;
  DOMstrings.stepFormPanels.forEach(elem => {
    if (elem.classList.contains('js-active')) {
      activePanel = elem;
    }
  });
  return activePanel;
};

// Open active panel (and close inactive panels)
const setActivePanel = activePanelNum => {
  removeClasses(DOMstrings.stepFormPanels, 'js-active');
  DOMstrings.stepFormPanels.forEach((elem, index) => {
    if (index === activePanelNum) {
      elem.classList.add('js-active');
      setFormHeight(elem);
    }
  });
};

// Set form height equal to current panel height
const formHeight = activePanel => {
  const activePanelHeight = activePanel.offsetHeight;
  DOMstrings.stepsForm.style.height = `${activePanelHeight}px`;
};

const setFormHeight = () => {
  const activePanel = getActivePanel();
  formHeight(activePanel);
};

// Function to show an error message next to the field
const showError = (field, message) => {
  field.classList.add('field-error');
  let popup = field.nextElementSibling;
  if (!popup || !popup.classList.contains('popup-message')) {
    popup = document.createElement('span');
    popup.className = 'popup-message';
    field.parentNode.appendChild(popup);
  }
  popup.textContent = message;
  popup.style.color = 'red';
  popup.style.display = 'block';
};

// Function to clear previous error styles and messages
const clearErrors = () => {
  const fields = document.querySelectorAll('.field-error');
  fields.forEach(field => {
    field.classList.remove('field-error');
    const popup = field.nextElementSibling;
    if (popup && popup.classList.contains('popup-message')) {
      popup.style.display = 'none';
      popup.textContent = '';
    }
  });
};

// Function to validate required fields in the current panel
const validateFields = activePanel => {
  const requiredFields = activePanel.querySelectorAll(DOMstrings.formFields);
  let isValid = true;
  clearErrors();

  requiredFields.forEach(field => {
    if (field.hasAttribute('required') && !field.value.trim()) {
      showError(field, "* This field is required.");
      isValid = false;
    }
  });

  const overallErrorMessage = document.querySelector(DOMstrings.overallErrorMessage);
  if (!isValid) {
    overallErrorMessage.textContent = "Please fill in all required fields.";
    overallErrorMessage.style.display = 'block';
  } else {
    overallErrorMessage.style.display = 'none';
    overallErrorMessage.textContent = '';
  }

  return isValid;
};

// Function to move to the next step in the form
const moveToNextStep = () => {
  const currentPanel = document.querySelector('.js-active');
  const nextPanel = currentPanel.nextElementSibling;
  if (nextPanel) {
    currentPanel.classList.remove('js-active');
    nextPanel.classList.add('js-active');
    updateProgressButtons();
  }
};

// Function to update progress buttons based on the active panel
const updateProgressButtons = () => {
  const progressButtons = document.querySelectorAll('.multisteps-form__progress-btn');
  progressButtons.forEach((btn, index) => {
    btn.classList.remove('js-active');
    if (index === Array.from(progressButtons).indexOf(document.querySelector('.js-active'))) {
      btn.classList.add('js-active');
    }
  });
};

// Event Listeners

// Handle next button click with validation
document.querySelector('.js-btn-next').addEventListener('click', function (e) {
  e.preventDefault();
  const activePanel = getActivePanel();
  if (validateFields(activePanel)) {
    moveToNextStep();
  }
});

// Handle previous button click
document.querySelector('.js-btn-prev').addEventListener('click', function (e) {
  e.preventDefault();
  const currentPanel = document.querySelector('.js-active');
  const prevPanel = currentPanel.previousElementSibling;
  if (prevPanel) {
    currentPanel.classList.remove('js-active');
    prevPanel.classList.add('js-active');
    updateProgressButtons();
  }
});

// Set form height on load and resize
window.addEventListener('load', setFormHeight, false);
window.addEventListener('resize', setFormHeight, false);

// Handle step bar clicks
DOMstrings.stepsBar.addEventListener('click', e => {
  const eventTarget = e.target;
  if (!eventTarget.classList.contains(`${DOMstrings.stepsBtnClass}`)) {
    return;
  }
  const activeStep = getActiveStep(eventTarget);
  setActiveStep(activeStep);
  setActivePanel(activeStep);
});
