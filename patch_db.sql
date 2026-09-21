-- Patch script: apply to the live `test` database to bring it up to date.
-- Safe to run multiple times — uses IF NOT EXISTS / ALTER IGNORE patterns.
USE `test`;

-- 1. uploaded_files table (was missing, caused non-fatal log errors)
CREATE TABLE IF NOT EXISTS `uploaded_files` (
    `file_id`       INT AUTO_INCREMENT PRIMARY KEY,
    `original_name` VARCHAR(255) NOT NULL,
    `stored_name`   VARCHAR(255) NOT NULL,
    `total_rows`    INT DEFAULT 0,
    `uploaded_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_date`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. sort_order column on invoices (preserves source Excel row order)
ALTER TABLE `invoices`
    ADD COLUMN IF NOT EXISTS `sort_order` INT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS `uploaded_file_id` INT DEFAULT NULL;

-- 3. sort_order column on gst_releases
ALTER TABLE `gst_releases`
    ADD COLUMN IF NOT EXISTS `sort_order` INT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS `uploaded_file_id` INT DEFAULT NULL;

-- 4. uploaded_file_id on other tables
ALTER TABLE `credit_note`   ADD COLUMN IF NOT EXISTS `uploaded_file_id` INT DEFAULT NULL;
ALTER TABLE `hold_release`  ADD COLUMN IF NOT EXISTS `uploaded_file_id` INT DEFAULT NULL;

DELIMITER //

-- 5. SaveInvoice — 20 params (added p_sort_order)
DROP PROCEDURE IF EXISTS SaveInvoice //
CREATE PROCEDURE SaveInvoice(
    IN p_pmc_no         INT,
    IN p_village_id     INT,
    IN p_work_type      VARCHAR(255),
    IN p_invoice_details TEXT,
    IN p_invoice_date   DATE,
    IN p_invoice_no     VARCHAR(100),
    IN p_basic          DECIMAL(15,2),
    IN p_debit          DECIMAL(15,2),
    IN p_after_debit    DECIMAL(15,2),
    IN p_amount         DECIMAL(15,2),
    IN p_gst            DECIMAL(15,2),
    IN p_tds            DECIMAL(15,2),
    IN p_sd             DECIMAL(15,2),
    IN p_commission     DECIMAL(15,2),
    IN p_hydro          DECIMAL(15,2),
    IN p_gst_sd         DECIMAL(15,2),
    IN p_final          DECIMAL(15,2),
    IN p_subcontractor_id INT,
    IN p_is_extra       TINYINT,
    IN p_sort_order     INT
)
BEGIN
    INSERT INTO invoices (
        PMC_No, Village_Id, Work_Type, Invoice_Details, Invoice_Date, Invoice_No,
        Basic_Amount, Debit_Amount, After_Debit_Amount, Amount, GST_Amount, TDS_Amount,
        SD_Amount, On_Commission, Hydro_Testing, GST_SD_Amount, Final_Amount,
        Subcontractor_Id, Is_Extra, sort_order
    ) VALUES (
        p_pmc_no, p_village_id, p_work_type, p_invoice_details, p_invoice_date, p_invoice_no,
        p_basic, p_debit, p_after_debit, p_amount, p_gst, p_tds,
        p_sd, p_commission, p_hydro, p_gst_sd, p_final,
        p_subcontractor_id, p_is_extra, p_sort_order
    );
    SELECT LAST_INSERT_ID() AS invoice_id;
END //

-- 6. insertExtrapaymet — 10 params (added p_sort_order), writes to invoices (plural)
DROP PROCEDURE IF EXISTS insertExtrapaymet //
CREATE PROCEDURE insertExtrapaymet(
    IN p_pmc_no         INT,
    IN p_details        TEXT,
    IN p_basic          DECIMAL(15,2),
    IN p_debit          DECIMAL(15,2),
    IN p_after_debit    DECIMAL(15,2),
    IN p_gst            DECIMAL(15,2),
    IN p_amount         DECIMAL(15,2),
    IN p_final          DECIMAL(15,2),
    IN p_subcontractor_id INT,
    IN p_sort_order     INT
)
BEGIN
    INSERT INTO invoices (PMC_No, Invoice_Details, Basic_Amount, Debit_Amount,
        After_Debit_Amount, GST_Amount, Amount, Final_Amount, Subcontractor_Id,
        Is_Extra, sort_order)
    VALUES (p_pmc_no, p_details, p_basic, p_debit,
        p_after_debit, p_gst, p_amount, p_final, p_subcontractor_id,
        1, p_sort_order);
    SELECT LAST_INSERT_ID() AS invoice_id;
END //

-- 7. AddGSTReleaseFromExcel — 8 params (added p_sort_order)
DROP PROCEDURE IF EXISTS AddGSTReleaseFromExcel //
CREATE PROCEDURE AddGSTReleaseFromExcel(
    IN p_pmc_no        VARCHAR(100),
    IN p_invoice_no    VARCHAR(100),
    IN p_basic         DECIMAL(15,2),
    IN p_final         DECIMAL(15,2),
    IN p_total         DECIMAL(15,2),
    IN p_utr           VARCHAR(255),
    IN p_contractor_id INT,
    IN p_sort_order    INT
)
BEGIN
    INSERT INTO gst_releases (PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount, UTR, Contractor_ID, sort_order)
    VALUES (p_pmc_no, p_invoice_no, p_basic, p_final, p_total, p_utr, p_contractor_id, p_sort_order);
END //

-- 8. GetHoldTypesByContractor — reads from invoice_subcontractor_hold_join
DROP PROCEDURE IF EXISTS GetHoldTypesByContractor //
CREATE PROCEDURE GetHoldTypesByContractor(IN p_contractor_id INT)
BEGIN
    SELECT DISTINCT ht.hold_type_id, ht.hold_type
    FROM hold_types ht
    JOIN invoice_subcontractor_hold_join j ON ht.hold_type_id = j.hold_type_id
    WHERE j.Contractor_Id = p_contractor_id;
END //

-- 9. GetHoldAmountsByContractor — reads from invoice_subcontractor_hold_join
DROP PROCEDURE IF EXISTS GetHoldAmountsByContractor //
CREATE PROCEDURE GetHoldAmountsByContractor(IN p_contractor_id INT)
BEGIN
    SELECT j.Invoice_Id, j.hold_type_id, j.hold_amount
    FROM invoice_subcontractor_hold_join j WHERE j.Contractor_Id = p_contractor_id;
END //

-- 10. GetCreditNotesByContractor — reads from credit_note (singular)
DROP PROCEDURE IF EXISTS GetCreditNotesByContractor //
CREATE PROCEDURE GetCreditNotesByContractor(IN p_contractor_id INT)
BEGIN
    SELECT Credit_Note_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount,
           Payment_Amount, UTR
    FROM credit_note WHERE Contractor_Id = p_contractor_id;
END //

-- 11. NewGetCreditNotesByPMCNo — reads from credit_note (singular)
DROP PROCEDURE IF EXISTS NewGetCreditNotesByPMCNo //
CREATE PROCEDURE NewGetCreditNotesByPMCNo(IN p_pmc_no VARCHAR(100))
BEGIN
    SELECT Credit_Note_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount,
           Payment_Amount, UTR
    FROM credit_note WHERE PMC_No = p_pmc_no;
END //

DELIMITER ;
