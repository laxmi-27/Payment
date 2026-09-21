CREATE DATABASE IF NOT EXISTS `test`;
USE `test`;

-- ===================== TABLES =====================

CREATE TABLE IF NOT EXISTS `states` (
    `State_Id` INT AUTO_INCREMENT PRIMARY KEY,
    `State_Name` VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `districts` (
    `District_Id` INT AUTO_INCREMENT PRIMARY KEY,
    `District_Name` VARCHAR(255) NOT NULL,
    `State_Id` INT NOT NULL,
    FOREIGN KEY (`State_Id`) REFERENCES `states`(`State_Id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `blocks` (
    `Block_Id` INT AUTO_INCREMENT PRIMARY KEY,
    `Block_Name` VARCHAR(255) NOT NULL,
    `District_Id` INT NOT NULL,
    FOREIGN KEY (`District_Id`) REFERENCES `districts`(`District_Id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `villages` (
    `Village_Id` INT AUTO_INCREMENT PRIMARY KEY,
    `Village_Name` VARCHAR(255) NOT NULL,
    `Block_Id` INT NOT NULL,
    FOREIGN KEY (`Block_Id`) REFERENCES `blocks`(`Block_Id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `hold_types` (
    `hold_type_id` INT AUTO_INCREMENT PRIMARY KEY,
    `hold_type` VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `subcontractors` (
    `Contractor_Id` INT AUTO_INCREMENT PRIMARY KEY,
    `Contractor_Name` VARCHAR(255) NOT NULL,
    `Address` TEXT,
    `Mobile_No` VARCHAR(20),
    `PAN_No` VARCHAR(20),
    `Email` VARCHAR(255),
    `Gender` VARCHAR(10),
    `GST_Registration_Type` VARCHAR(50),
    `GST_No` VARCHAR(50),
    `Contractor_password` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `uploaded_files` (
    `file_id`       INT AUTO_INCREMENT PRIMARY KEY,
    `original_name` VARCHAR(255) NOT NULL,
    `stored_name`   VARCHAR(255) NOT NULL,
    `total_rows`    INT DEFAULT 0,
    `uploaded_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_date`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `invoices` (
    `Invoice_Id`        INT AUTO_INCREMENT PRIMARY KEY,
    `PMC_No`            INT,
    `Village_Id`        INT,
    `Work_Type`         VARCHAR(255),
    `Invoice_Details`   TEXT,
    `Invoice_Date`      DATE,
    `Invoice_No`        VARCHAR(100),
    `Basic_Amount`      DECIMAL(15,2) DEFAULT 0,
    `Debit_Amount`      DECIMAL(15,2) DEFAULT 0,
    `After_Debit_Amount` DECIMAL(15,2) DEFAULT 0,
    `Amount`            DECIMAL(15,2) DEFAULT 0,
    `GST_Amount`        DECIMAL(15,2) DEFAULT 0,
    `TDS_Amount`        DECIMAL(15,2) DEFAULT 0,
    `SD_Amount`         DECIMAL(15,2) DEFAULT 0,
    `On_Commission`     DECIMAL(15,2) DEFAULT 0,
    `Hydro_Testing`     DECIMAL(15,2) DEFAULT 0,
    `GST_SD_Amount`     DECIMAL(15,2) DEFAULT 0,
    `Final_Amount`      DECIMAL(15,2) DEFAULT 0,
    `Subcontractor_Id`  INT,
    `Is_Extra`          TINYINT DEFAULT 0,
    `sort_order`        INT DEFAULT NULL,
    `uploaded_file_id`  INT DEFAULT NULL,
    FOREIGN KEY (`Village_Id`)       REFERENCES `villages`(`Village_Id`),
    FOREIGN KEY (`Subcontractor_Id`) REFERENCES `subcontractors`(`Contractor_Id`)
);

-- Holds per invoice per contractor (the active holds table)
CREATE TABLE IF NOT EXISTS `invoice_subcontractor_hold_join` (
    `id`           INT AUTO_INCREMENT PRIMARY KEY,
    `Contractor_Id` INT,
    `Invoice_Id`   INT,
    `hold_type_id` INT,
    `hold_amount`  DECIMAL(15,2) DEFAULT 0,
    FOREIGN KEY (`Invoice_Id`)    REFERENCES `invoices`(`Invoice_Id`) ON DELETE CASCADE,
    FOREIGN KEY (`hold_type_id`)  REFERENCES `hold_types`(`hold_type_id`),
    FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors`(`Contractor_Id`)
);

-- Active payments table (singular); FK to invoices (plural)
CREATE TABLE IF NOT EXISTS `payment` (
    `Payment_Id`         INT AUTO_INCREMENT PRIMARY KEY,
    `PMC_No`             INT,
    `invoice_no`         VARCHAR(100),
    `Payment_Amount`     DECIMAL(15,2) DEFAULT 0,
    `TDS_Payment_Amount` DECIMAL(15,2) DEFAULT 0,
    `Total_Amount`       DECIMAL(15,2) DEFAULT 0,
    `UTR`                VARCHAR(255),
    `Invoice_Id`         INT,
    FOREIGN KEY (`Invoice_Id`) REFERENCES `invoices`(`Invoice_Id`)
);

CREATE TABLE IF NOT EXISTS `gst_releases` (
    `GST_Release_Id` INT AUTO_INCREMENT PRIMARY KEY,
    `PMC_No`         VARCHAR(100),
    `Invoice_No`     VARCHAR(100),
    `Basic_Amount`   DECIMAL(15,2) DEFAULT 0,
    `Final_Amount`   DECIMAL(15,2) DEFAULT 0,
    `Total_Amount`   DECIMAL(15,2) DEFAULT 0,
    `UTR`            VARCHAR(255),
    `Contractor_ID`  INT,
    `sort_order`     INT DEFAULT NULL,
    `uploaded_file_id` INT DEFAULT NULL,
    FOREIGN KEY (`Contractor_ID`) REFERENCES `subcontractors`(`Contractor_Id`)
);

CREATE TABLE IF NOT EXISTS `credit_note` (
    `Credit_Note_Id`    INT AUTO_INCREMENT PRIMARY KEY,
    `PMC_No`            VARCHAR(100),
    `Invoice_No`        VARCHAR(100),
    `Invoice_Details`   TEXT,
    `Basic_Amount`      DECIMAL(15,2) DEFAULT 0,
    `Debit_Amount`      DECIMAL(15,2) DEFAULT 0,
    `After_Debit_Amount` DECIMAL(15,2) DEFAULT 0,
    `GST_Amount`        DECIMAL(15,2) DEFAULT 0,
    `Amount`            DECIMAL(15,2) DEFAULT 0,
    `Final_Amount`      DECIMAL(15,2) DEFAULT 0,
    `Payment_Amount`    DECIMAL(15,2) DEFAULT 0,
    `Total_Amount`      DECIMAL(15,2) DEFAULT 0,
    `UTR`               VARCHAR(255),
    `Contractor_Id`     INT,
    `uploaded_file_id`  INT DEFAULT NULL,
    FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors`(`Contractor_Id`)
);

CREATE TABLE IF NOT EXISTS `hold_release` (
    `Hold_Release_Id` INT AUTO_INCREMENT PRIMARY KEY,
    `PMC_No`          VARCHAR(100),
    `Invoice_No`      VARCHAR(100),
    `Invoice_Details` TEXT,
    `Basic_Amount`    DECIMAL(15,2) DEFAULT 0,
    `Final_Amount`    DECIMAL(15,2) DEFAULT 0,
    `Total_Amount`    DECIMAL(15,2) DEFAULT 0,
    `UTR`             VARCHAR(255) UNIQUE,
    `Contractor_Id`   INT,
    `uploaded_file_id` INT DEFAULT NULL,
    FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors`(`Contractor_Id`)
);

CREATE TABLE IF NOT EXISTS `items` (
    `item_id`   INT AUTO_INCREMENT PRIMARY KEY,
    `item_type` INT NOT NULL,
    `item_name` VARCHAR(255) NOT NULL
);

-- ===================== STORED PROCEDURES =====================

DELIMITER //

-- ── STATE ────────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS CheckStateExists //
CREATE PROCEDURE CheckStateExists(IN p_name VARCHAR(255))
BEGIN SELECT * FROM states WHERE State_Name = p_name LIMIT 1; END //

DROP PROCEDURE IF EXISTS SaveState //
CREATE PROCEDURE SaveState(IN p_name VARCHAR(255))
BEGIN INSERT INTO states (State_Name) VALUES (p_name); END //

DROP PROCEDURE IF EXISTS GetAllStates //
CREATE PROCEDURE GetAllStates()
BEGIN SELECT State_Id, State_Name FROM states ORDER BY State_Name; END //

DROP PROCEDURE IF EXISTS UpdateStateById //
CREATE PROCEDURE UpdateStateById(IN p_id INT, IN p_name VARCHAR(255))
BEGIN UPDATE states SET State_Name = p_name WHERE State_Id = p_id; END //

DROP PROCEDURE IF EXISTS GetStateByID //
CREATE PROCEDURE GetStateByID(IN p_id INT)
BEGIN SELECT State_Id, State_Name FROM states WHERE State_Id = p_id; END //

DROP PROCEDURE IF EXISTS DeleteState //
CREATE PROCEDURE DeleteState(IN p_id INT)
BEGIN DELETE FROM states WHERE State_Id = p_id; END //

-- ── DISTRICT ─────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS GetDistrictByNameAndState //
CREATE PROCEDURE GetDistrictByNameAndState(IN p_name VARCHAR(255), IN p_state_id INT)
BEGIN SELECT * FROM districts WHERE District_Name = p_name AND State_Id = p_state_id LIMIT 1; END //

DROP PROCEDURE IF EXISTS SaveDistrict //
CREATE PROCEDURE SaveDistrict(IN p_name VARCHAR(255), IN p_state_id INT)
BEGIN INSERT INTO districts (District_Name, State_Id) VALUES (p_name, p_state_id); END //

DROP PROCEDURE IF EXISTS GetAllDistricts //
CREATE PROCEDURE GetAllDistricts()
BEGIN
    SELECT d.District_Id, d.District_Name, d.State_Id, s.State_Name
    FROM districts d JOIN states s ON d.State_Id = s.State_Id
    ORDER BY d.District_Name;
END //

DROP PROCEDURE IF EXISTS UpdateDistrict //
CREATE PROCEDURE UpdateDistrict(IN p_id INT, IN p_state_id INT, IN p_name VARCHAR(255))
BEGIN UPDATE districts SET District_Name = p_name, State_Id = p_state_id WHERE District_Id = p_id; END //

DROP PROCEDURE IF EXISTS GetDistrictDataByID //
CREATE PROCEDURE GetDistrictDataByID(IN p_id INT)
BEGIN
    SELECT d.District_Id, d.District_Name, d.State_Id, s.State_Name
    FROM districts d JOIN states s ON d.State_Id = s.State_Id
    WHERE d.District_Id = p_id;
END //

DROP PROCEDURE IF EXISTS DeleteDistrict //
CREATE PROCEDURE DeleteDistrict(IN p_id INT)
BEGIN DELETE FROM districts WHERE District_Id = p_id; END //

-- ── BLOCK ────────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS GetBlockByNameAndDistrict //
CREATE PROCEDURE GetBlockByNameAndDistrict(IN p_name VARCHAR(255), IN p_district_id INT)
BEGIN SELECT * FROM blocks WHERE Block_Name = p_name AND District_Id = p_district_id LIMIT 1; END //

DROP PROCEDURE IF EXISTS SaveBlock //
CREATE PROCEDURE SaveBlock(IN p_name VARCHAR(255), IN p_district_id INT)
BEGIN INSERT INTO blocks (Block_Name, District_Id) VALUES (p_name, p_district_id); END //

DROP PROCEDURE IF EXISTS GetAllBlock //
CREATE PROCEDURE GetAllBlock()
BEGIN
    SELECT b.Block_Id, b.Block_Name, b.District_Id, d.District_Name
    FROM blocks b JOIN districts d ON b.District_Id = d.District_Id
    ORDER BY b.Block_Name;
END //

DROP PROCEDURE IF EXISTS UpdateBlockById //
CREATE PROCEDURE UpdateBlockById(IN p_id INT, IN p_district_id INT, IN p_name VARCHAR(255))
BEGIN UPDATE blocks SET Block_Name = p_name, District_Id = p_district_id WHERE Block_Id = p_id; END //

DROP PROCEDURE IF EXISTS GetBlockDataByID //
CREATE PROCEDURE GetBlockDataByID(IN p_id INT)
BEGIN
    SELECT b.Block_Id, b.Block_Name, b.District_Id, d.District_Name
    FROM blocks b JOIN districts d ON b.District_Id = d.District_Id
    WHERE b.Block_Id = p_id;
END //

DROP PROCEDURE IF EXISTS DeleteBlock //
CREATE PROCEDURE DeleteBlock(IN p_id INT)
BEGIN DELETE FROM blocks WHERE Block_Id = p_id; END //

-- ── VILLAGE ──────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS GetVillageByNameAndBlock //
CREATE PROCEDURE GetVillageByNameAndBlock(IN p_name VARCHAR(255), IN p_block_id INT)
BEGIN SELECT * FROM villages WHERE Village_Name = p_name AND Block_Id = p_block_id LIMIT 1; END //

DROP PROCEDURE IF EXISTS SaveVillage //
CREATE PROCEDURE SaveVillage(IN p_name VARCHAR(255), IN p_block_id INT)
BEGIN INSERT INTO villages (Village_Name, Block_Id) VALUES (p_name, p_block_id); END //

DROP PROCEDURE IF EXISTS GetAllVillages //
CREATE PROCEDURE GetAllVillages()
BEGIN
    SELECT v.Village_Id, v.Village_Name, v.Block_Id, b.Block_Name,
           d.District_Id, d.District_Name, s.State_Id, s.State_Name
    FROM villages v
    JOIN blocks    b ON v.Block_Id    = b.Block_Id
    JOIN districts d ON b.District_Id = d.District_Id
    JOIN states    s ON d.State_Id    = s.State_Id
    ORDER BY v.Village_Name;
END //

DROP PROCEDURE IF EXISTS UpdateVillage //
CREATE PROCEDURE UpdateVillage(IN p_id INT, IN p_block_id INT, IN p_name VARCHAR(255))
BEGIN UPDATE villages SET Village_Name = p_name, Block_Id = p_block_id WHERE Village_Id = p_id; END //

DROP PROCEDURE IF EXISTS GetVillageDetailsById //
CREATE PROCEDURE GetVillageDetailsById(IN p_id INT)
BEGIN
    SELECT v.Village_Id, v.Village_Name, v.Block_Id, b.Block_Name,
           d.District_Id, d.District_Name, s.State_Id, s.State_Name
    FROM villages v
    JOIN blocks    b ON v.Block_Id    = b.Block_Id
    JOIN districts d ON b.District_Id = d.District_Id
    JOIN states    s ON d.State_Id    = s.State_Id
    WHERE v.Village_Id = p_id;
END //

DROP PROCEDURE IF EXISTS DeleteVillage //
CREATE PROCEDURE DeleteVillage(IN p_id INT)
BEGIN DELETE FROM villages WHERE Village_Id = p_id; END //

-- Returns Village_Id for (block_id, village_name) — used during Excel upload
DROP PROCEDURE IF EXISTS GetVillageId //
CREATE PROCEDURE GetVillageId(IN p_block_id INT, IN p_village_name VARCHAR(255))
BEGIN
    SELECT Village_Id FROM villages
    WHERE Block_Id = p_block_id AND LOWER(Village_Name) = LOWER(p_village_name)
    LIMIT 1;
END //

DROP PROCEDURE IF EXISTS GetVillageIdByName //
CREATE PROCEDURE GetVillageIdByName(IN p_name VARCHAR(255))
BEGIN SELECT Village_Id FROM villages WHERE Village_Name = p_name LIMIT 1; END //

-- ── HOLD TYPES ───────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS CheckHoldTypeExists //
CREATE PROCEDURE CheckHoldTypeExists(IN p_name VARCHAR(255))
BEGIN SELECT * FROM hold_types WHERE hold_type = p_name LIMIT 1; END //

DROP PROCEDURE IF EXISTS SaveHoldType //
CREATE PROCEDURE SaveHoldType(IN p_name VARCHAR(255))
BEGIN INSERT INTO hold_types (hold_type) VALUES (p_name); END //

DROP PROCEDURE IF EXISTS GetAllHoldTypes //
CREATE PROCEDURE GetAllHoldTypes()
BEGIN SELECT hold_type_id, hold_type FROM hold_types ORDER BY hold_type; END //

DROP PROCEDURE IF EXISTS GetHoldTypesById //
CREATE PROCEDURE GetHoldTypesById(IN p_id INT)
BEGIN SELECT hold_type_id, hold_type FROM hold_types WHERE hold_type_id = p_id; END //

DROP PROCEDURE IF EXISTS UpdateHoldTypeById //
CREATE PROCEDURE UpdateHoldTypeById(IN p_id INT, IN p_name VARCHAR(255))
BEGIN UPDATE hold_types SET hold_type = p_name WHERE hold_type_id = p_id; END //

DROP PROCEDURE IF EXISTS DeleteHoldType //
CREATE PROCEDURE DeleteHoldType(IN p_id INT)
BEGIN DELETE FROM hold_types WHERE hold_type_id = p_id; END //

DROP PROCEDURE IF EXISTS GetHoldTypeIdByName //
CREATE PROCEDURE GetHoldTypeIdByName(IN p_name VARCHAR(255))
BEGIN SELECT hold_type_id FROM hold_types WHERE hold_type = p_name LIMIT 1; END //

DROP PROCEDURE IF EXISTS InsertHoldType //
CREATE PROCEDURE InsertHoldType(IN p_hold_type VARCHAR(255), OUT p_hold_type_id INT)
BEGIN
    INSERT INTO hold_types (hold_type) VALUES (p_hold_type);
    SET p_hold_type_id = LAST_INSERT_ID();
END //

-- ── SUBCONTRACTOR ────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS GetSubcontractorByName //
CREATE PROCEDURE GetSubcontractorByName(IN p_name VARCHAR(255))
BEGIN SELECT * FROM subcontractors WHERE Contractor_Name = p_name LIMIT 1; END //

DROP PROCEDURE IF EXISTS SaveContractor //
CREATE PROCEDURE SaveContractor(
    IN p_name VARCHAR(255), IN p_address TEXT, IN p_mobile VARCHAR(20),
    IN p_pan VARCHAR(20), IN p_email VARCHAR(255), IN p_gender VARCHAR(10),
    IN p_gst_type VARCHAR(50), IN p_gst_no VARCHAR(50), IN p_password VARCHAR(255)
)
BEGIN
    INSERT INTO subcontractors
        (Contractor_Name, Address, Mobile_No, PAN_No, Email, Gender, GST_Registration_Type, GST_No, Contractor_password)
    VALUES
        (p_name, p_address, p_mobile, p_pan, p_email, p_gender, p_gst_type, p_gst_no, p_password);
END //

DROP PROCEDURE IF EXISTS GetAllSubcontractors //
CREATE PROCEDURE GetAllSubcontractors()
BEGIN
    SELECT Contractor_Id, Contractor_Name, Address, Mobile_No, PAN_No, Email, Gender, GST_Registration_Type, GST_No
    FROM subcontractors ORDER BY Contractor_Name;
END //

DROP PROCEDURE IF EXISTS GetSubcontractorById //
CREATE PROCEDURE GetSubcontractorById(IN p_id INT)
BEGIN
    SELECT Contractor_Id, Contractor_Name, Address, Mobile_No, PAN_No, Email,
           Gender, GST_Registration_Type, GST_No, Contractor_password
    FROM subcontractors WHERE Contractor_Id = p_id;
END //

DROP PROCEDURE IF EXISTS UpdateSubcontractor //
CREATE PROCEDURE UpdateSubcontractor(
    IN p_id INT, IN p_name VARCHAR(255), IN p_address TEXT, IN p_mobile VARCHAR(20),
    IN p_pan VARCHAR(20), IN p_email VARCHAR(255), IN p_gender VARCHAR(10),
    IN p_gst_type VARCHAR(50), IN p_gst_no VARCHAR(50), IN p_password VARCHAR(255)
)
BEGIN
    UPDATE subcontractors SET
        Contractor_Name = p_name, Address = p_address, Mobile_No = p_mobile,
        PAN_No = p_pan, Email = p_email, Gender = p_gender,
        GST_Registration_Type = p_gst_type, GST_No = p_gst_no,
        Contractor_password = p_password
    WHERE Contractor_Id = p_id;
END //

DROP PROCEDURE IF EXISTS DeleteSubcontractor //
CREATE PROCEDURE DeleteSubcontractor(IN p_id INT)
BEGIN DELETE FROM subcontractors WHERE Contractor_Id = p_id; END //

DROP PROCEDURE IF EXISTS SearchContractorsByName //
CREATE PROCEDURE SearchContractorsByName(IN p_query VARCHAR(255))
BEGIN
    SELECT Contractor_Id, Contractor_Name, Address, Mobile_No, PAN_No, Email
    FROM subcontractors WHERE Contractor_Name LIKE CONCAT('%', p_query, '%');
END //

-- ── INVOICE ──────────────────────────────────────────────────────

-- 20 params: adds p_sort_order for source-file row-order preservation
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

-- Extra-payment rows (rows with no village/work keyword): writes to invoices (plural)
-- 10 params: adds p_sort_order
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

DROP PROCEDURE IF EXISTS GetAllInvoiceDetails //
CREATE PROCEDURE GetAllInvoiceDetails()
BEGIN
    SELECT i.Invoice_Id, i.PMC_No, i.Invoice_No, i.Invoice_Date, i.Invoice_Details, i.Work_Type,
           v.Village_Name, i.Village_Id, i.Basic_Amount, i.Debit_Amount, i.After_Debit_Amount,
           i.Amount, i.GST_Amount, i.TDS_Amount, i.SD_Amount, i.On_Commission, i.Hydro_Testing,
           i.GST_SD_Amount, i.Final_Amount, i.Subcontractor_Id, s.Contractor_Name
    FROM invoices i
    LEFT JOIN villages v      ON i.Village_Id      = v.Village_Id
    LEFT JOIN subcontractors s ON i.Subcontractor_Id = s.Contractor_Id
    ORDER BY i.Invoice_Id DESC;
END //

DROP PROCEDURE IF EXISTS GetInvoiceDetailsById //
CREATE PROCEDURE GetInvoiceDetailsById(IN p_id INT)
BEGIN
    SELECT i.Invoice_Id, i.PMC_No, i.Invoice_No, i.Invoice_Date, i.Invoice_Details, i.Work_Type,
           v.Village_Name, i.Village_Id, i.Basic_Amount, i.Debit_Amount, i.After_Debit_Amount,
           i.Amount, i.GST_Amount, i.TDS_Amount, i.SD_Amount, i.On_Commission, i.Hydro_Testing,
           i.GST_SD_Amount, i.Final_Amount, i.Subcontractor_Id, s.Contractor_Name
    FROM invoices i
    LEFT JOIN villages v      ON i.Village_Id      = v.Village_Id
    LEFT JOIN subcontractors s ON i.Subcontractor_Id = s.Contractor_Id
    WHERE i.Invoice_Id = p_id;
END //

DROP PROCEDURE IF EXISTS UpdateInvoice //
CREATE PROCEDURE UpdateInvoice(
    IN p_pmc_no INT, IN p_village_id INT, IN p_work_type VARCHAR(255),
    IN p_invoice_details TEXT, IN p_invoice_date DATE, IN p_invoice_no VARCHAR(100),
    IN p_basic DECIMAL(15,2), IN p_debit DECIMAL(15,2), IN p_after_debit DECIMAL(15,2),
    IN p_amount DECIMAL(15,2), IN p_gst DECIMAL(15,2), IN p_tds DECIMAL(15,2),
    IN p_sd DECIMAL(15,2), IN p_commission DECIMAL(15,2), IN p_hydro DECIMAL(15,2),
    IN p_gst_sd DECIMAL(15,2), IN p_final DECIMAL(15,2), IN p_invoice_id INT
)
BEGIN
    UPDATE invoices SET
        PMC_No = p_pmc_no, Village_Id = p_village_id, Work_Type = p_work_type,
        Invoice_Details = p_invoice_details, Invoice_Date = p_invoice_date, Invoice_No = p_invoice_no,
        Basic_Amount = p_basic, Debit_Amount = p_debit, After_Debit_Amount = p_after_debit,
        Amount = p_amount, GST_Amount = p_gst, TDS_Amount = p_tds, SD_Amount = p_sd,
        On_Commission = p_commission, Hydro_Testing = p_hydro, GST_SD_Amount = p_gst_sd,
        Final_Amount = p_final
    WHERE Invoice_Id = p_invoice_id;
END //

DROP PROCEDURE IF EXISTS GetInvoicePMCById //
CREATE PROCEDURE GetInvoicePMCById(IN p_id INT)
BEGIN SELECT PMC_No, Invoice_No FROM invoices WHERE Invoice_Id = p_id; END //

DROP PROCEDURE IF EXISTS DeleteInvoice //
CREATE PROCEDURE DeleteInvoice(IN p_id INT)
BEGIN
    DELETE FROM invoice_subcontractor_hold_join WHERE Invoice_Id = p_id;
    DELETE FROM payment WHERE Invoice_Id = p_id;
    DELETE FROM invoices WHERE Invoice_Id = p_id;
END //

DROP PROCEDURE IF EXISTS GetInvoicesByContractor //
CREATE PROCEDURE GetInvoicesByContractor(IN p_contractor_id INT)
BEGIN
    SELECT i.Invoice_Id, i.PMC_No, i.Invoice_No, i.Invoice_Date, i.Basic_Amount,
           i.Final_Amount, v.Village_Name
    FROM invoices i LEFT JOIN villages v ON i.Village_Id = v.Village_Id
    WHERE i.Subcontractor_Id = p_contractor_id ORDER BY i.Invoice_Id DESC;
END //

DROP PROCEDURE IF EXISTS GetInvoicesByContractorOrPMCNo //
CREATE PROCEDURE GetInvoicesByContractorOrPMCNo(IN p_contractor_id INT, IN p_pmc_no INT)
BEGIN
    SELECT i.Invoice_Id, i.PMC_No, i.Invoice_No, i.Invoice_Date, i.Invoice_Details, i.Work_Type,
           v.Village_Name, i.Basic_Amount, i.Debit_Amount, i.After_Debit_Amount, i.Amount,
           i.GST_Amount, i.TDS_Amount, i.SD_Amount, i.On_Commission, i.Hydro_Testing,
           i.GST_SD_Amount, i.Final_Amount, i.Subcontractor_Id
    FROM invoices i LEFT JOIN villages v ON i.Village_Id = v.Village_Id
    WHERE (p_contractor_id IS NOT NULL AND i.Subcontractor_Id = p_contractor_id)
       OR (p_pmc_no IS NOT NULL AND i.PMC_No = p_pmc_no)
    ORDER BY i.PMC_No, i.Invoice_Id;
END //

DROP PROCEDURE IF EXISTS GetInvoiceId //
CREATE PROCEDURE GetInvoiceId(IN p_subcontractor_id INT, IN p_pmc_no INT, IN p_invoice_no VARCHAR(100))
BEGIN
    SELECT Invoice_Id FROM invoices
    WHERE Subcontractor_Id = p_subcontractor_id AND PMC_No = p_pmc_no AND Invoice_No = p_invoice_no
    LIMIT 1;
END //

-- ── HOLD JOIN ────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS InsertHoldJoinData //
CREATE PROCEDURE InsertHoldJoinData(
    IN p_contractor_id INT, IN p_invoice_id INT,
    IN p_hold_type_id INT, IN p_hold_amount DECIMAL(15,2)
)
BEGIN
    INSERT INTO invoice_subcontractor_hold_join (Contractor_Id, Invoice_Id, hold_type_id, hold_amount)
    VALUES (p_contractor_id, p_invoice_id, p_hold_type_id, p_hold_amount);
END //

DROP PROCEDURE IF EXISTS GetHoldAmountsByInvoiceId //
CREATE PROCEDURE GetHoldAmountsByInvoiceId(IN p_invoice_id INT)
BEGIN
    SELECT j.id, j.Contractor_Id, j.Invoice_Id, j.hold_type_id, j.hold_amount, ht.hold_type
    FROM invoice_subcontractor_hold_join j
    JOIN hold_types ht ON j.hold_type_id = ht.hold_type_id
    WHERE j.Invoice_Id = p_invoice_id;
END //

-- ── PAYMENT ──────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS SavePayment //
CREATE PROCEDURE SavePayment(
    IN p_pmc_no    INT,
    IN p_invoice_no VARCHAR(100),
    IN p_amount    DECIMAL(15,2),
    IN p_tds       DECIMAL(15,2),
    IN p_total     DECIMAL(15,2),
    IN p_utr       VARCHAR(255),
    IN p_invoice_id INT
)
BEGIN
    INSERT INTO payment (PMC_No, invoice_no, Payment_Amount, TDS_Payment_Amount, Total_Amount, UTR, Invoice_Id)
    VALUES (p_pmc_no, p_invoice_no, p_amount, p_tds, p_total, p_utr, p_invoice_id);
END //

DROP PROCEDURE IF EXISTS GetAllPayments //
CREATE PROCEDURE GetAllPayments()
BEGIN
    SELECT Payment_Id, PMC_No, invoice_no AS Invoice_No,
           Payment_Amount, TDS_Payment_Amount, Total_Amount, UTR
    FROM payment ORDER BY Payment_Id DESC;
END //

DROP PROCEDURE IF EXISTS GetPaymentById //
CREATE PROCEDURE GetPaymentById(IN p_id INT)
BEGIN
    SELECT Payment_Id, PMC_No, invoice_no AS Invoice_No,
           Payment_Amount, TDS_Payment_Amount, Total_Amount, UTR
    FROM payment WHERE Payment_Id = p_id;
END //

DROP PROCEDURE IF EXISTS UpdatePayment //
CREATE PROCEDURE UpdatePayment(
    IN p_payment_id INT, IN p_pmc_no INT, IN p_invoice_no VARCHAR(100),
    IN p_amount DECIMAL(15,2), IN p_tds DECIMAL(15,2),
    IN p_total DECIMAL(15,2), IN p_utr VARCHAR(255)
)
BEGIN
    UPDATE payment SET
        PMC_No = p_pmc_no, invoice_no = p_invoice_no, Payment_Amount = p_amount,
        TDS_Payment_Amount = p_tds, Total_Amount = p_total, UTR = p_utr
    WHERE Payment_Id = p_payment_id;
END //

DROP PROCEDURE IF EXISTS DeletePayment //
CREATE PROCEDURE DeletePayment(IN p_id INT)
BEGIN DELETE FROM payment WHERE Payment_Id = p_id; END //

DROP PROCEDURE IF EXISTS GetPaymentsByPMC //
CREATE PROCEDURE GetPaymentsByPMC(IN p_pmc_no INT)
BEGIN
    SELECT Payment_Id, PMC_No, invoice_no AS Invoice_No,
           Payment_Amount, TDS_Payment_Amount, Total_Amount AS Total_amount, UTR
    FROM payment WHERE PMC_No = p_pmc_no;
END //

DROP PROCEDURE IF EXISTS GetPayments //
CREATE PROCEDURE GetPayments(IN p_contractor_id INT)
BEGIN
    SELECT p.Payment_Id, p.PMC_No, p.invoice_no AS Invoice_No,
           p.Payment_Amount, p.TDS_Payment_Amount, p.Total_Amount AS Total_amount, p.UTR
    FROM payment p JOIN invoices i ON p.Invoice_Id = i.Invoice_Id
    WHERE i.Subcontractor_Id = p_contractor_id;
END //

-- ── GST RELEASES ─────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS CheckGSTReleaseExists //
CREATE PROCEDURE CheckGSTReleaseExists(IN p_pmc_no VARCHAR(100), IN p_invoice_no VARCHAR(100))
BEGIN SELECT * FROM gst_releases WHERE PMC_No = p_pmc_no AND Invoice_No = p_invoice_no LIMIT 1; END //

-- 8 params: adds p_sort_order for source-file row-order preservation
DROP PROCEDURE IF EXISTS AddGSTReleaseFromExcel //
CREATE PROCEDURE AddGSTReleaseFromExcel(
    IN p_pmc_no       VARCHAR(100),
    IN p_invoice_no   VARCHAR(100),
    IN p_basic        DECIMAL(15,2),
    IN p_final        DECIMAL(15,2),
    IN p_total        DECIMAL(15,2),
    IN p_utr          VARCHAR(255),
    IN p_contractor_id INT,
    IN p_sort_order   INT
)
BEGIN
    INSERT INTO gst_releases (PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount, UTR, Contractor_ID, sort_order)
    VALUES (p_pmc_no, p_invoice_no, p_basic, p_final, p_total, p_utr, p_contractor_id, p_sort_order);
END //

DROP PROCEDURE IF EXISTS UpdateGSTRelease //
CREATE PROCEDURE UpdateGSTRelease(
    IN p_pmc_no VARCHAR(100), IN p_invoice_no VARCHAR(100),
    IN p_basic DECIMAL(15,2), IN p_final DECIMAL(15,2), IN p_total DECIMAL(15,2),
    IN p_utr VARCHAR(255), IN p_gst_release_id INT
)
BEGIN
    UPDATE gst_releases SET
        PMC_No = p_pmc_no, Invoice_No = p_invoice_no, Basic_Amount = p_basic,
        Final_Amount = p_final, Total_Amount = p_total, UTR = p_utr
    WHERE GST_Release_Id = p_gst_release_id;
END //

DROP PROCEDURE IF EXISTS DeleteGSTReleaseById //
CREATE PROCEDURE DeleteGSTReleaseById(IN p_id INT)
BEGIN DELETE FROM gst_releases WHERE GST_Release_Id = p_id; END //

DROP PROCEDURE IF EXISTS GetAllGSTReleases //
CREATE PROCEDURE GetAllGSTReleases()
BEGIN
    SELECT GST_Release_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount, UTR, Contractor_ID
    FROM gst_releases ORDER BY GST_Release_Id DESC;
END //

DROP PROCEDURE IF EXISTS GetGSTReleaseById //
CREATE PROCEDURE GetGSTReleaseById(IN p_id INT)
BEGIN
    SELECT GST_Release_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount, UTR, Contractor_ID
    FROM gst_releases WHERE GST_Release_Id = p_id;
END //

DROP PROCEDURE IF EXISTS GetGSTReleaseDetailsByPMC //
CREATE PROCEDURE GetGSTReleaseDetailsByPMC(IN p_pmc_no VARCHAR(100))
BEGIN
    SELECT GST_Release_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount, UTR, Contractor_ID
    FROM gst_releases WHERE PMC_No = p_pmc_no;
END //

DROP PROCEDURE IF EXISTS GstReleasesByContractorId //
CREATE PROCEDURE GstReleasesByContractorId(IN p_contractor_id INT)
BEGIN
    SELECT GST_Release_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount, UTR, Contractor_ID
    FROM gst_releases WHERE Contractor_ID = p_contractor_id;
END //

-- ── CREDIT NOTES ─────────────────────────────────────────────────

-- 13 params: writes to credit_note (singular)
DROP PROCEDURE IF EXISTS AddCreditNoteFromExcel //
CREATE PROCEDURE AddCreditNoteFromExcel(
    IN p_pmc_no         VARCHAR(100),
    IN p_details        TEXT,
    IN p_basic          DECIMAL(15,2),
    IN p_debit          DECIMAL(15,2),
    IN p_after_debit    DECIMAL(15,2),
    IN p_gst            DECIMAL(15,2),
    IN p_amount         DECIMAL(15,2),
    IN p_final          DECIMAL(15,2),
    IN p_payment_amount DECIMAL(15,2),
    IN p_total          DECIMAL(15,2),
    IN p_utr            VARCHAR(255),
    IN p_contractor_id  INT,
    IN p_invoice_no     VARCHAR(100)
)
BEGIN
    INSERT INTO credit_note (
        PMC_No, Invoice_Details, Basic_Amount, Debit_Amount, After_Debit_Amount,
        GST_Amount, Amount, Final_Amount, Payment_Amount, Total_Amount, UTR,
        Contractor_Id, Invoice_No
    ) VALUES (
        p_pmc_no, p_details, p_basic, p_debit, p_after_debit,
        p_gst, p_amount, p_final, p_payment_amount, p_total, p_utr,
        p_contractor_id, p_invoice_no
    );
END //

DROP PROCEDURE IF EXISTS NewGetCreditNotesByPMCNo //
CREATE PROCEDURE NewGetCreditNotesByPMCNo(IN p_pmc_no VARCHAR(100))
BEGIN
    SELECT Credit_Note_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount,
           Payment_Amount, UTR
    FROM credit_note WHERE PMC_No = p_pmc_no;
END //

DROP PROCEDURE IF EXISTS GetCreditNotesByContractor //
CREATE PROCEDURE GetCreditNotesByContractor(IN p_contractor_id INT)
BEGIN
    SELECT Credit_Note_Id, PMC_No, Invoice_No, Basic_Amount, Final_Amount, Total_Amount,
           Payment_Amount, UTR
    FROM credit_note WHERE Contractor_Id = p_contractor_id;
END //

-- ── HOLD RELEASES ────────────────────────────────────────────────

-- 8 params: writes to hold_release
DROP PROCEDURE IF EXISTS AddHoldReleaseFromExcel //
CREATE PROCEDURE AddHoldReleaseFromExcel(
    IN p_pmc_no        VARCHAR(100),
    IN p_invoice_no    VARCHAR(100),
    IN p_details       TEXT,
    IN p_basic         DECIMAL(15,2),
    IN p_final         DECIMAL(15,2),
    IN p_total         DECIMAL(15,2),
    IN p_utr           VARCHAR(255),
    IN p_contractor_id INT
)
BEGIN
    INSERT INTO hold_release (PMC_No, Invoice_No, Invoice_Details, Basic_Amount, Final_Amount, Total_Amount, UTR, Contractor_Id)
    VALUES (p_pmc_no, p_invoice_no, p_details, p_basic, p_final, p_total, p_utr, p_contractor_id);
END //

-- ── REPORT / LOOKUP ──────────────────────────────────────────────

DROP PROCEDURE IF EXISTS GetContractorInfo //
CREATE PROCEDURE GetContractorInfo(IN p_contractor_id INT)
BEGIN
    SELECT Contractor_Id, Contractor_Name, Address, Mobile_No, PAN_No, Email,
           Gender, GST_Registration_Type, GST_No
    FROM subcontractors WHERE Contractor_Id = p_contractor_id;
END //

DROP PROCEDURE IF EXISTS GetContractorInfoByPmcNo //
CREATE PROCEDURE GetContractorInfoByPmcNo(IN p_pmc_no INT)
BEGIN
    SELECT DISTINCT s.Contractor_Id, s.Contractor_Name, s.Address, s.Mobile_No, s.PAN_No,
           s.Email, s.Gender, s.GST_Registration_Type, s.GST_No
    FROM subcontractors s JOIN invoices i ON s.Contractor_Id = i.Subcontractor_Id
    WHERE i.PMC_No = p_pmc_no LIMIT 1;
END //

-- Uses invoice_subcontractor_hold_join (the active holds table)
DROP PROCEDURE IF EXISTS GetHoldTypesByContractor //
CREATE PROCEDURE GetHoldTypesByContractor(IN p_contractor_id INT)
BEGIN
    SELECT DISTINCT ht.hold_type_id, ht.hold_type
    FROM hold_types ht
    JOIN invoice_subcontractor_hold_join j ON ht.hold_type_id = j.hold_type_id
    WHERE j.Contractor_Id = p_contractor_id;
END //

DROP PROCEDURE IF EXISTS GetHoldAmountsByContractor //
CREATE PROCEDURE GetHoldAmountsByContractor(IN p_contractor_id INT)
BEGIN
    SELECT j.Invoice_Id, j.hold_type_id, j.hold_amount
    FROM invoice_subcontractor_hold_join j WHERE j.Contractor_Id = p_contractor_id;
END //

DROP PROCEDURE IF EXISTS GetHoldAmountsAndHoldTypeByCtr //
CREATE PROCEDURE GetHoldAmountsAndHoldTypeByCtr(IN p_contractor_id INT)
BEGIN
    SELECT j.hold_type_id, ht.hold_type, SUM(j.hold_amount) AS hold_amount
    FROM invoice_subcontractor_hold_join j
    JOIN hold_types ht ON j.hold_type_id = ht.hold_type_id
    WHERE j.Contractor_Id = p_contractor_id
    GROUP BY j.hold_type_id, ht.hold_type;
END //

DROP PROCEDURE IF EXISTS GetHoldReleaseByPMC //
CREATE PROCEDURE GetHoldReleaseByPMC(IN p_pmc_no INT)
BEGIN
    SELECT j.Invoice_Id, j.hold_type_id, ht.hold_type, j.hold_amount
    FROM invoice_subcontractor_hold_join j
    JOIN hold_types ht ON j.hold_type_id = ht.hold_type_id
    JOIN invoices i ON j.Invoice_Id = i.Invoice_Id
    WHERE i.PMC_No = p_pmc_no;
END //

DROP PROCEDURE IF EXISTS search_contractor_info //
CREATE PROCEDURE search_contractor_info(
    IN p_name VARCHAR(255), IN p_pmc_no INT, IN p_state VARCHAR(255),
    IN p_district VARCHAR(255), IN p_block VARCHAR(255), IN p_village VARCHAR(255),
    IN p_year_from INT, IN p_year_to INT
)
BEGIN
    SELECT DISTINCT s.Contractor_Id, s.Contractor_Name, s.Address, s.Mobile_No, s.Email,
           i.PMC_No, i.Invoice_Id, v.Village_Name, b.Block_Name, d.District_Name, st.State_Name,
           i.Basic_Amount, i.Final_Amount, i.Invoice_Date
    FROM subcontractors s
    JOIN invoices i ON s.Contractor_Id = i.Subcontractor_Id
    LEFT JOIN villages  v  ON i.Village_Id   = v.Village_Id
    LEFT JOIN blocks    b  ON v.Block_Id     = b.Block_Id
    LEFT JOIN districts d  ON b.District_Id  = d.District_Id
    LEFT JOIN states    st ON d.State_Id     = st.State_Id
    WHERE (p_name IS NULL OR s.Contractor_Name LIKE CONCAT('%', p_name, '%'))
      AND (p_pmc_no IS NULL OR i.PMC_No = p_pmc_no)
      AND (p_state IS NULL OR st.State_Name = p_state)
      AND (p_district IS NULL OR d.District_Name = p_district)
      AND (p_block IS NULL OR b.Block_Name = p_block)
      AND (p_village IS NULL OR v.Village_Name = p_village)
      AND (p_year_from IS NULL OR YEAR(i.Invoice_Date) >= p_year_from)
      AND (p_year_to IS NULL OR YEAR(i.Invoice_Date) <= p_year_to)
    ORDER BY s.Contractor_Name, i.PMC_No;
END //

-- ── MISC ─────────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS GetItemsByType //
CREATE PROCEDURE GetItemsByType(IN p_type INT)
BEGIN SELECT item_id, item_name FROM items WHERE item_type = p_type ORDER BY item_name; END //

DROP PROCEDURE IF EXISTS InsertItem //
CREATE PROCEDURE InsertItem(IN p_type INT, IN p_name VARCHAR(255))
BEGIN INSERT INTO items (item_type, item_name) VALUES (p_type, p_name); END //

DROP PROCEDURE IF EXISTS UpdateItem //
CREATE PROCEDURE UpdateItem(IN p_type INT, IN p_id INT, IN p_name VARCHAR(255))
BEGIN UPDATE items SET item_name = p_name WHERE item_id = p_id AND item_type = p_type; END //

DROP PROCEDURE IF EXISTS DeleteItem //
CREATE PROCEDURE DeleteItem(IN p_type INT, IN p_id INT)
BEGIN DELETE FROM items WHERE item_id = p_id AND item_type = p_type; END //

DELIMITER ;
