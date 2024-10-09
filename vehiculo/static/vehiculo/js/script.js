function expand(identifier) {
    let target_content = document.getElementById(identifier);
    let target = document.getElementById("target-img");
    target.src = target_content.src;
    target.alt = target_content.alt;
    let current_value = Number(target_content.id.split("-").at(-1));
    let element_array = document.querySelectorAll(".next-img");
    let total_elements = document.querySelectorAll(".gallery").length;
    if (element_array.length === 2 && !Number.isNaN(current_value)) {
        element_array[0].id = `left--imagen-${current_value - 1 > 0 ? current_value - 1 : total_elements}`;
        element_array[1].id = `right--imagen-${current_value + 1 > total_elements ? 1 : current_value + 1}`;
    }
    let state = document.getElementById("image-target-dialog"); 
    if (!state.open) {
        state.show();
    }
}

function next_img(operand) {
    expand(operand.split("--").at(-1));
}