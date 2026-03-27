$(document).ready(function () {
    // Create a module to manage hold amounts
    window.holdAmountModule = {
        holdCount: 0,
        holdTypes: [],
        
        init: function() {
            this.loadHoldTypes();
            this.setupEventListeners();
        },
        
        loadHoldTypes: function() {
            $.ajax({
                url: '/get_hold_types',
                method: 'GET',
                dataType: 'json',
                success: (data) => {
                    this.holdTypes = data;
                    $("#add_hold_amount").prop('disabled', false);
                },
                error: (err) => {
                    console.error('Failed to load hold types', err);
                }
            });
        },
        
        setupEventListeners: function() {
            $("#add_hold_amount").click(() => this.addHoldAmountField());
            $(document).on("click", ".remove-hold", (e) => this.removeHoldAmountField(e));
            $(document).on("change", ".hold-type-dropdown", () => this.refreshDropdowns());
            $(document).on("input", "input[name='hold_amount[]']", () => this.triggerHoldAmountChanged());
        },
        
        addHoldAmountField: function() {
            this.holdCount++;
            $("#hold_amount_container").append(`
                <div class="hold-amount-field" id="hold_${this.holdCount}">
                    <select name="hold_type[]" class="hold-type-dropdown" required>
                        ${this.generateOptions()}
                    </select>
                    <input type="number" step="0.01" name="hold_amount[]" 
                           class="hold-amount-input" placeholder="Hold Amount" required>
                    <button type="button" class="remove-hold" data-id="hold_${this.holdCount}">X</button>
                </div>
            `);
            this.refreshDropdowns();
            this.triggerHoldAmountChanged();
        },
        
        removeHoldAmountField: function(e) {
            const id = $(e.target).attr("data-id");
            $(`#${id}`).remove();
            this.refreshDropdowns();
            this.triggerHoldAmountChanged();
        },
        
        generateOptions: function(selectedForThisDropdown = '') {
            const selectedValues = $("select[name='hold_type[]']").map(function() {
                return $(this).val();
            }).get();

            let options = '<option value="">Select Hold Type</option>';
            this.holdTypes.forEach((type) => {
                if (!selectedValues.includes(type.hold_type) || type.hold_type === selectedForThisDropdown) {
                    options += `<option value="${type.hold_type}">${type.hold_type}</option>`;
                }
            });
            return options;
        },
        
        refreshDropdowns: function() {
            $("select[name='hold_type[]']").each(function() {
                const currentVal = $(this).val();
                $(this).html(window.holdAmountModule.generateOptions(currentVal));
                $(this).val(currentVal);
            });
        },
        
        getTotalHoldAmount: function() {
            let total = 0;
            $("input[name='hold_amount[]']").each(function() {
                total += parseFloat($(this).val()) || 0;
            });
            return total;
        },
        
        triggerHoldAmountChanged: function() {
            const event = new Event('holdAmountChanged');
            document.dispatchEvent(event);
        }
    };

    // Initialize the module
    window.holdAmountModule.init();
});