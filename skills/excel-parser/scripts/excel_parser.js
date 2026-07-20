#!/usr/bin/env node
// -*- coding: utf-8 -*-
/**
 * Excel 配表解析脚本 (Node.js 版本) - 直接读取游戏配表 Excel 文件
 * 支持名将杀项目统一的 4 行表头结构
 *
 * 依赖: npm install -g xlsx
 * 使用: node excel_parser.js <action> [options]
 */

const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// 名将杀项目表头结构常量
const HEADER_ROWS = 4;  // 前4行是表头
const CHS_NAME_ROW = 0; // 第1行: 中文名称
const TYPE_ROW = 1;     // 第2行: 字段类型
const FIELD_ROW = 2;    // 第3行: 字段名
const EXPORT_ROW = 3;   // 第4行: 导出标识
const DATA_START = 5;   // 第5行开始是数据 (1-based Excel row)

/**
 * 加载 Excel 文件
 * @param {string} filePath - Excel 文件路径
 * @param {string} [sheetName] - 指定 Sheet 名称
 * @returns {{workbook: object, sheet: object, actualSheetName: string}}
 */
function loadExcel(filePath, sheetName) {
    const workbook = XLSX.readFile(filePath, { cellFormula: false, cellNF: false });

    let targetSheetName = sheetName;
    if (!targetSheetName) {
        targetSheetName = workbook.SheetNames[0];
    }

    // 尝试直接匹配
    let sheet = workbook.Sheets[targetSheetName];
    let actualSheetName = targetSheetName;

    if (!sheet) {
        // 尝试后缀匹配（支持 "中文|英文" 格式）
        for (const name of workbook.SheetNames) {
            if (name.includes('|')) {
                const parts = name.split('|');
                if (parts.some(p => p.trim() === targetSheetName)) {
                    sheet = workbook.Sheets[name];
                    actualSheetName = name;
                    break;
                }
            }
            if (name.includes(targetSheetName)) {
                sheet = workbook.Sheets[name];
                actualSheetName = name;
                break;
            }
        }
    }

    if (!sheet) {
        const available = workbook.SheetNames.join(', ');
        throw new Error(`Sheet '${sheetName}' 不存在。可用: ${available}`);
    }

    return { workbook, sheet, actualSheetName };
}

/**
 * 获取单元格值（处理合并单元格）
 * @param {object} sheet - XLSX sheet 对象
 * @param {number} row - 行号 (1-based)
 * @param {number} col - 列号 (1-based)
 * @returns {string}
 */
function getCellValue(sheet, row, col) {
    const cellRef = XLSX.utils.encode_cell({ r: row - 1, c: col - 1 });
    const cell = sheet[cellRef];
    if (!cell) return '';
    const val = cell.v;
    return val !== null && val !== undefined ? String(val) : '';
}

/**
 * 获取 Sheet 的最大列数
 * @param {object} sheet - XLSX sheet 对象
 * @returns {number}
 */
function getMaxCol(sheet) {
    const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1');
    return range.e.c + 1; // 转换为 1-based
}

/**
 * 获取 Sheet 的最大行数
 * @param {object} sheet - XLSX sheet 对象
 * @returns {number}
 */
function getMaxRow(sheet) {
    const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1');
    return range.e.r + 1; // 转换为 1-based
}

/**
 * 获取 Excel 文件的所有 Sheet 信息
 * @param {string} filePath - Excel 文件路径
 * @returns {object}
 */
function getSheetInfo(filePath) {
    const workbook = XLSX.readFile(filePath, { cellFormula: false, cellNF: false });
    const result = {
        filePath: filePath,
        sheets: []
    };

    for (const name of workbook.SheetNames) {
        const sheet = workbook.Sheets[name];
        result.sheets.push({
            name: name,
            maxRow: getMaxRow(sheet),
            maxCol: getMaxCol(sheet)
        });
    }

    return result;
}

/**
 * 获取 Sheet 的列定义信息
 * @param {string} filePath - Excel 文件路径
 * @param {string} sheetName - Sheet 名称
 * @returns {object}
 */
function getColumnInfo(filePath, sheetName) {
    const { sheet, actualSheetName } = loadExcel(filePath, sheetName);
    const maxCol = getMaxCol(sheet);
    const columns = [];

    for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
        const chsName = getCellValue(sheet, 1, colIdx);
        const fieldType = getCellValue(sheet, 2, colIdx);
        const fieldName = getCellValue(sheet, 3, colIdx);
        const exportTag = getCellValue(sheet, 4, colIdx);

        let status = 'NORMAL';
        if (fieldType === '#') {
            status = 'COMMENT';
        } else if (fieldType && fieldType.startsWith('E#')) {
            status = 'ENUM';
        } else if (!fieldName) {
            status = 'EMPTY';
        }

        columns.push({
            index: colIdx,
            chsName: chsName || '',
            fieldType: fieldType || '',
            fieldName: fieldName || '',
            exportTag: exportTag || '',
            status: status
        });
    }

    return {
        filePath: filePath,
        sheetName: actualSheetName,
        columns: columns
    };
}

/**
 * 预览 Sheet 前 N 行数据
 * @param {string} filePath - Excel 文件路径
 * @param {string} sheetName - Sheet 名称
 * @param {number} [rows=10] - 预览行数
 * @returns {object}
 */
function previewSheet(filePath, sheetName, rows = 10) {
    const { sheet, actualSheetName } = loadExcel(filePath, sheetName);
    const maxCol = getMaxCol(sheet);
    const maxRow = getMaxRow(sheet);

    const headers = [];
    for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
        const chsName = getCellValue(sheet, 1, colIdx);
        headers.push(chsName || `Col${colIdx}`);
    }

    const dataRows = [];
    const endRow = Math.min(DATA_START + rows - 1, maxRow);
    for (let rowIdx = DATA_START; rowIdx <= endRow; rowIdx++) {
        const rowData = [];
        for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
            rowData.push(getCellValue(sheet, rowIdx, colIdx));
        }
        dataRows.push(rowData);
    }

    return {
        filePath: filePath,
        sheetName: actualSheetName,
        headers: headers,
        dataRows: dataRows,
        totalRows: Math.max(0, maxRow - HEADER_ROWS),
        returnedRows: dataRows.length
    };
}

/**
 * 查询指定行范围的数据
 * @param {string} filePath - Excel 文件路径
 * @param {string} sheetName - Sheet 名称
 * @param {number} startRow - 起始数据行号（从1开始）
 * @param {number} [endRow] - 结束数据行号
 * @param {boolean} [includeHeader=false] - 是否包含表头
 * @returns {object}
 */
function queryRange(filePath, sheetName, startRow, endRow, includeHeader = false) {
    const { sheet, actualSheetName } = loadExcel(filePath, sheetName);
    const maxCol = getMaxCol(sheet);
    const maxRow = getMaxRow(sheet);

    // start_row 是数据行号（从1开始），转换为 Excel 行号
    const excelStart = DATA_START + startRow - 1;
    let excelEnd = endRow ? DATA_START + endRow - 1 : maxRow;

    if (excelStart > maxRow) {
        return { error: `起始行 ${startRow} 超出数据范围` };
    }

    excelEnd = Math.min(excelEnd, maxRow);

    const result = {
        filePath: filePath,
        sheetName: actualSheetName,
        startRow: startRow,
        endRow: startRow + (excelEnd - excelStart),
        totalRows: Math.max(0, maxRow - HEADER_ROWS),
        headers: [],
        dataRows: []
    };

    if (includeHeader) {
        const headers = [];
        for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
            const chsName = getCellValue(sheet, 1, colIdx);
            const fieldName = getCellValue(sheet, 3, colIdx);
            headers.push(chsName || fieldName || `Col${colIdx}`);
        }
        result.headers = headers;
    }

    for (let rowIdx = excelStart; rowIdx <= excelEnd; rowIdx++) {
        const rowData = [];
        for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
            rowData.push(getCellValue(sheet, rowIdx, colIdx));
        }
        result.dataRows.push(rowData);
    }

    return result;
}

/**
 * 根据条件过滤数据
 * @param {string} filePath - Excel 文件路径
 * @param {string} sheetName - Sheet 名称
 * @param {Array} conditions - 过滤条件数组
 * @param {boolean} [includeHeader=false] - 是否包含表头
 * @returns {object}
 */
function filterData(filePath, sheetName, conditions, includeHeader = false) {
    const { sheet, actualSheetName } = loadExcel(filePath, sheetName);
    const maxCol = getMaxCol(sheet);
    const maxRow = getMaxRow(sheet);

    // 构建列名到索引的映射
    const colMap = {};
    for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
        const chsName = getCellValue(sheet, 1, colIdx);
        const fieldName = getCellValue(sheet, 3, colIdx);
        if (chsName) colMap[chsName] = colIdx;
        if (fieldName) colMap[fieldName] = colIdx;
    }

    const result = {
        filePath: filePath,
        sheetName: actualSheetName,
        totalRows: Math.max(0, maxRow - HEADER_ROWS),
        matchedRows: 0,
        headers: [],
        dataRows: []
    };

    if (includeHeader) {
        const headers = [];
        for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
            const chsName = getCellValue(sheet, 1, colIdx);
            const fieldName = getCellValue(sheet, 3, colIdx);
            headers.push(chsName || fieldName || `Col${colIdx}`);
        }
        result.headers = headers;
    }

    for (let rowIdx = DATA_START; rowIdx <= maxRow; rowIdx++) {
        let match = true;
        for (const cond of conditions) {
            const colName = cond.columnName || '';
            const value = cond.value || '';
            const operator = cond.operator || 'eq';

            if (!(colName in colMap)) {
                match = false;
                break;
            }

            const colIdx = colMap[colName];
            const cellStr = getCellValue(sheet, rowIdx, colIdx);

            switch (operator) {
                case 'eq':
                    match = cellStr === value;
                    break;
                case 'neq':
                    match = cellStr !== value;
                    break;
                case 'contains':
                    match = cellStr.includes(value);
                    break;
                case 'startsWith':
                    match = cellStr.startsWith(value);
                    break;
                case 'endsWith':
                    match = cellStr.endsWith(value);
                    break;
                default:
                    match = cellStr === value;
            }

            if (!match) break;
        }

        if (match) {
            const rowData = [];
            for (let colIdx = 1; colIdx <= maxCol; colIdx++) {
                rowData.push(getCellValue(sheet, rowIdx, colIdx));
            }
            result.dataRows.push(rowData);
        }
    }

    result.matchedRows = result.dataRows.length;
    return result;
}

/**
 * 扫描目录下的所有 Excel 文件
 * @param {string} dirPath - 目录路径
 * @returns {object}
 */
function scanExcelDir(dirPath) {
    const files = [];
    const entries = fs.readdirSync(dirPath);

    for (const entry of entries.sort()) {
        if (!entry.endsWith('.xlsx') && !entry.endsWith('.xls')) {
            continue;
        }
        if (entry.startsWith('~$')) continue; // 跳过临时文件

        const fullPath = path.join(dirPath, entry);
        try {
            const workbook = XLSX.readFile(fullPath, { cellFormula: false, cellNF: false });
            files.push({
                fileName: entry,
                filePath: fullPath,
                sheets: workbook.SheetNames
            });
        } catch (e) {
            files.push({
                fileName: entry,
                filePath: fullPath,
                error: e.message
            });
        }
    }

    return { dirPath: dirPath, files: files };
}

/**
 * 对比两个 Excel 文件的差异（用于 git diff）
 * @param {string} fileA - 文件A路径
 * @param {string} fileB - 文件B路径
 * @param {string} [sheetName] - 指定 Sheet 名称
 * @returns {object}
 */
function diffExcel(fileA, fileB, sheetName) {
    const { sheet: sheetA, actualSheetName: nameA } = loadExcel(fileA, sheetName);
    const { sheet: sheetB, actualSheetName: nameB } = loadExcel(fileB, sheetName || nameA);

    const maxColA = getMaxCol(sheetA);
    const maxColB = getMaxCol(sheetB);
    const maxRowA = getMaxRow(sheetA);
    const maxRowB = getMaxRow(sheetB);

    // 获取表头信息
    const headersA = [];
    const headersB = [];
    for (let colIdx = 1; colIdx <= maxColA; colIdx++) {
        headersA.push({
            chsName: getCellValue(sheetA, 1, colIdx),
            fieldType: getCellValue(sheetA, 2, colIdx),
            fieldName: getCellValue(sheetA, 3, colIdx),
            exportTag: getCellValue(sheetA, 4, colIdx)
        });
    }
    for (let colIdx = 1; colIdx <= maxColB; colIdx++) {
        headersB.push({
            chsName: getCellValue(sheetB, 1, colIdx),
            fieldType: getCellValue(sheetB, 2, colIdx),
            fieldName: getCellValue(sheetB, 3, colIdx),
            exportTag: getCellValue(sheetB, 4, colIdx)
        });
    }

    // 对比数据行
    const maxDataRowA = Math.max(0, maxRowA - HEADER_ROWS);
    const maxDataRowB = Math.max(0, maxRowB - HEADER_ROWS);
    const maxDataRows = Math.max(maxDataRowA, maxDataRowB);
    const maxCols = Math.max(maxColA, maxColB);

    const addedRows = [];
    const deletedRows = [];
    const modifiedRows = [];

    for (let dataRowIdx = 1; dataRowIdx <= maxDataRows; dataRowIdx++) {
        const excelRowA = DATA_START + dataRowIdx - 1;
        const excelRowB = DATA_START + dataRowIdx - 1;

        const rowA = [];
        const rowB = [];

        for (let colIdx = 1; colIdx <= maxCols; colIdx++) {
            rowA.push(excelRowA <= maxRowA ? getCellValue(sheetA, excelRowA, colIdx) : null);
            rowB.push(excelRowB <= maxRowB ? getCellValue(sheetB, excelRowB, colIdx) : null);
        }

        const rowAEmpty = rowA.every(v => v === '' || v === null);
        const rowBEmpty = rowB.every(v => v === '' || v === null);

        if (rowAEmpty && !rowBEmpty) {
            addedRows.push({ rowIndex: dataRowIdx, data: rowB.filter(v => v !== null) });
        } else if (!rowAEmpty && rowBEmpty) {
            deletedRows.push({ rowIndex: dataRowIdx, data: rowA.filter(v => v !== null) });
        } else if (!rowAEmpty && !rowBEmpty) {
            // 检查是否有差异
            const diffs = [];
            for (let colIdx = 0; colIdx < maxCols; colIdx++) {
                const valA = rowA[colIdx] || '';
                const valB = rowB[colIdx] || '';
                if (valA !== valB) {
                    const fieldName = colIdx < headersA.length ? headersA[colIdx].fieldName :
                                     (colIdx < headersB.length ? headersB[colIdx].fieldName : `Col${colIdx + 1}`);
                    diffs.push({
                        column: fieldName,
                        oldValue: valA,
                        newValue: valB
                    });
                }
            }
            if (diffs.length > 0) {
                modifiedRows.push({ rowIndex: dataRowIdx, diffs: diffs });
            }
        }
    }

    return {
        fileA: fileA,
        fileB: fileB,
        sheetName: nameA || nameB,
        headersA: headersA,
        headersB: headersB,
        summary: {
            totalRowsA: maxDataRowA,
            totalRowsB: maxDataRowB,
            addedRows: addedRows.length,
            deletedRows: deletedRows.length,
            modifiedRows: modifiedRows.length
        },
        added: addedRows,
        deleted: deletedRows,
        modified: modifiedRows
    };
}

/**
 * 解析命令行参数
 */
function parseArgs() {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        return null;
    }

    const action = args[0];
    const options = {};

    for (let i = 1; i < args.length; i++) {
        const arg = args[i];
        if (arg === '--file' || arg === '-f') {
            options.file = args[++i];
        } else if (arg === '--dir' || arg === '-d') {
            options.dir = args[++i];
        } else if (arg === '--sheet' || arg === '-s') {
            options.sheet = args[++i];
        } else if (arg === '--rows' || arg === '-r') {
            options.rows = parseInt(args[++i], 10);
        } else if (arg === '--start') {
            options.start = parseInt(args[++i], 10);
        } else if (arg === '--end') {
            options.end = parseInt(args[++i], 10);
        } else if (arg === '--header') {
            options.header = true;
        } else if (arg === '--conditions' || arg === '-c') {
            options.conditions = args[++i];
        } else if (arg === '--file-a') {
            options.fileA = args[++i];
        } else if (arg === '--file-b') {
            options.fileB = args[++i];
        }
    }

    return { action, options };
}

/**
 * 打印帮助信息
 */
function printHelp() {
    console.log(`
Excel 配表解析工具 (Node.js 版本)

用法: node excel_parser.js <action> [options]

操作类型:
  scan      扫描目录下的所有 Excel 文件
  sheets    获取 Excel 文件的所有 Sheet
  columns   获取 Sheet 的列定义信息
  preview   预览 Sheet 前 N 行数据
  query     查询指定行范围的数据
  filter    根据条件过滤数据
  diff      对比两个 Excel 文件的差异

选项:
  --file, -f <path>      Excel 文件路径
  --dir, -d <path>       Excel 目录路径
  --sheet, -s <name>     Sheet 名称
  --rows, -r <num>       预览行数 (默认: 10)
  --start <num>          起始数据行号 (默认: 1)
  --end <num>            结束数据行号
  --header               包含表头
  --conditions, -c <json> 过滤条件 JSON 字符串
  --file-a <path>        对比文件A
  --file-b <path>        对比文件B

示例:
  node excel_parser.js scan --dir D:/work/config/excel
  node excel_parser.js sheets --file Hero.xlsx
  node excel_parser.js columns --file Hero.xlsx --sheet Hero
  node excel_parser.js preview --file Hero.xlsx --sheet Hero --rows 20
  node excel_parser.js query --file Hero.xlsx --sheet Hero --start 1 --end 10 --header
  node excel_parser.js filter --file Hero.xlsx --sheet Hero --conditions '[{"columnName":"Quality","value":"5","operator":"eq"}]' --header
  node excel_parser.js diff --file-a old.xlsx --file-b new.xlsx --sheet Hero
`);
}

/**
 * 主函数
 */
function main() {
    const parsed = parseArgs();
    if (!parsed) {
        printHelp();
        process.exit(1);
    }

    const { action, options } = parsed;
    let result;

    try {
        switch (action) {
            case 'scan':
                if (!options.dir) {
                    console.error('错误: scan 操作需要 --dir 参数');
                    process.exit(1);
                }
                result = scanExcelDir(options.dir);
                break;

            case 'sheets':
                if (!options.file) {
                    console.error('错误: sheets 操作需要 --file 参数');
                    process.exit(1);
                }
                result = getSheetInfo(options.file);
                break;

            case 'columns':
                if (!options.file || !options.sheet) {
                    console.error('错误: columns 操作需要 --file 和 --sheet 参数');
                    process.exit(1);
                }
                result = getColumnInfo(options.file, options.sheet);
                break;

            case 'preview':
                if (!options.file || !options.sheet) {
                    console.error('错误: preview 操作需要 --file 和 --sheet 参数');
                    process.exit(1);
                }
                result = previewSheet(options.file, options.sheet, options.rows || 10);
                break;

            case 'query':
                if (!options.file || !options.sheet) {
                    console.error('错误: query 操作需要 --file 和 --sheet 参数');
                    process.exit(1);
                }
                result = queryRange(
                    options.file,
                    options.sheet,
                    options.start || 1,
                    options.end,
                    options.header || false
                );
                break;

            case 'filter':
                if (!options.file || !options.sheet || !options.conditions) {
                    console.error('错误: filter 操作需要 --file, --sheet 和 --conditions 参数');
                    process.exit(1);
                }
                result = filterData(
                    options.file,
                    options.sheet,
                    JSON.parse(options.conditions),
                    options.header || false
                );
                break;

            case 'diff':
                if (!options.fileA || !options.fileB) {
                    console.error('错误: diff 操作需要 --file-a 和 --file-b 参数');
                    process.exit(1);
                }
                result = diffExcel(options.fileA, options.fileB, options.sheet);
                break;

            default:
                console.error(`错误: 未知的操作类型 '${action}'`);
                printHelp();
                process.exit(1);
        }

        console.log(JSON.stringify(result, null, 2));
    } catch (e) {
        console.error(JSON.stringify({ error: e.message }, null, 2));
        process.exit(1);
    }
}

main();
