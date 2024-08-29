document.addEventListener('DOMContentLoaded', () => {
  function checkFilters() {
    console.log("In checking filters");
    const form = document.getElementById("filterForm");
    const output = document.getElementById("filter-output");
  
    // Clear any previous output
    output.innerHTML = "Testing Button Click<br>";
  
    // Drainage 
    let drainage = getCheckedValues("drainage[]");
    if (drainage.length > 0) {
      output.innerHTML += "<b>Drainage:<b> " + drainage.join(', ') + "<br>";
    }
   
    // Shearing
    let shearing = getCheckedValues("shearing[]");
    if (shearing.length > 0) {
      output.innerHTML += "<b>Shearing:<b> " + shearing.join(', ') + "<br>";
    }
  
    // Anisotropy
    let anisotropy = getCheckedValues("anisotropy[]");
    if (anisotropy.length > 0) {
      output.innerHTML += "<b>Anisotropy:<b> " + anisotropy.join(', ') + "<br>";
    }
    const minAnisotropyInput = document.getElementById("filter-aniso-min");
    const maxAnisotropyInput = document.getElementById("filter-aniso-max");
    const minAnisotropyValue = minAnisotropyInput.value;
    const maxAnisotropyValue = maxAnisotropyInput.value;
    output.innerHTML += `<b>Min Anisotropy:</b> ${minAnisotropyValue}<br>`;
    output.innerHTML += `<b>Max Anisotropy:</b> ${maxAnisotropyValue}<br>`;
  
  
    // Consolidation
    const minConsolidationInput = document.getElementById("filter-con-min");
    const maxConsolidationInput = document.getElementById("filter-con-max");
    const minConsolidationValue = minConsolidationInput.value;
    const maxConsolidationValue = maxConsolidationInput.value;
    output.innerHTML += `<b>Min Consolidation:</b> ${minConsolidationValue}<br>`;
    output.innerHTML += `<b>Max Consolidation:</b> ${maxConsolidationValue}<br>`; 
  
    // Availability
    let availability = getCheckedValues("availability[]");
    if (availability.length > 0) {
      output.innerHTML += "<b>Availability:<b> " + availability.join(', ') + "<br>";
    }
  
  }
  
  function getCheckedValues(name) {
    const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
    return Array.from(checkboxes).map(checkbox => checkbox.value);
  }
  
  const button = document.getElementById('check-btn');
  if (button) {
    button.addEventListener('click', checkFilters);
  } else {
    console.error('Button with id "check-btn" not found');
  }

});