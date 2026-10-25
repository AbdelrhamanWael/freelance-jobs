if (document.getElementById('add-question-btn')) {
    let questionCount = 0;
    const questionsList = document.getElementById('questions-list');
    const addQuestionBtn = document.getElementById('add-question-btn');

    addQuestionBtn.addEventListener('click', function() {
        questionCount++;
        const qDiv = document.createElement('div');
        qDiv.className = 'exam-question-box';
        qDiv.innerHTML = `
            <div class="question-header">
                <button type="button" class="remove-question-btn" title="Remove this question">&times;</button>
            </div>

            <div class="question-images-container"></div>

            <div class="form-group" style="flex-direction:row;">
                <input type="text" name="questions[${questionCount}][text]" placeholder="Enter question text">
                <label class="upload-label">
                    <span class="upload-icon" aria-hidden="true">📷</span>
                    <input type="file" name="questions[${questionCount}][image]" accept="image/*" class="question-image-input" style="display:none;">
                </label>
            </div>

            <div class="choices-list"></div>
            <button type="button" class="add-choice-btn"><i class='fas fa-plus'></i> Add Choice</button>
        `;
        questionsList.appendChild(qDiv);

        const choicesListDiv = qDiv.querySelector('.choices-list');
        addChoice(choicesListDiv, questionCount);
        addChoice(choicesListDiv, questionCount);

        // Add choice button
        qDiv.querySelector('.add-choice-btn').addEventListener('click', function() {
            addChoice(choicesListDiv, questionCount);
        });

        // Remove question button
        qDiv.querySelector('.remove-question-btn').addEventListener('click', function() {
            qDiv.remove();
        });

        // ✅ Image preview for question
        const fileInput = qDiv.querySelector('.question-image-input');
        const previewContainer = qDiv.querySelector('.question-images-container');

        fileInput.addEventListener('change', function(event) {
            previewContainer.innerHTML = ''; // clear previous
            const file = event.target.files[0];
            if (file) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.maxWidth = "150px";
                img.style.maxHeight = "150px";
                img.style.marginBottom = "8px";
                img.style.border = "1px solid #ccc";
                img.style.borderRadius = "6px";
                previewContainer.appendChild(img);
            }
        });
    });

    function addChoice(choicesList, qNum) {
        const choiceCount = choicesList.querySelectorAll('.form-group-choice').length;

        const cDiv = document.createElement('div');
        cDiv.className = 'form-group-choice';
        cDiv.innerHTML = `
            <div>
                <div class="images-container"></div>
                <div class="choice-container">
                    <input type="radio" name="questions[${qNum}][correct_choice]" value="${choiceCount}" class="correct-choice-radio" title="Mark as correct" required>
                    
                    <input type="text" name="questions[${qNum}][choices][${choiceCount}][text]" placeholder="Enter choice text" class="choice-input">

                    <label class="upload-label">
                        <span class="upload-icon" aria-hidden="true">🖼️</span>
                        <input type="file" name="questions[${qNum}][choices][${choiceCount}][image]" accept="image/*" class="choice-image-input" style="display:none;">
                    </label>

                    <button type="button" class="remove-choice-btn" title="Remove choice">&times;</button>
                </div>
            </div>
        `;
        choicesList.appendChild(cDiv);

        // remove button
        cDiv.querySelector('.remove-choice-btn').addEventListener('click', function() {
            cDiv.remove();
        });

        // preview
        const fileInput = cDiv.querySelector('.choice-image-input');
        const imagesContainer = cDiv.querySelector('.images-container');

        fileInput.addEventListener('change', function(event) {
            imagesContainer.innerHTML = '';
            const file = event.target.files[0];
            if (file) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.maxWidth = "120px";
                img.style.maxHeight = "120px";
                img.style.marginTop = "8px";
                img.style.border = "1px solid #ccc";
                img.style.borderRadius = "6px";
                imagesContainer.appendChild(img);
            }
        });
    }


}