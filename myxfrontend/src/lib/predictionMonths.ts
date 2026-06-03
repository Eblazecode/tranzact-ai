export type PredictionMonthOption = {
  label: string;
  month: number;
  year: number;
  value: string;
};

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function addMonths(date: Date, months: number) {
  return new Date(date.getFullYear(), date.getMonth() + months, 1);
}

export function buildPredictionMonthOptions(startDate: string, endDate: string): PredictionMonthOption[] {
  if (!startDate || !endDate) return [];

  const start = new Date(startDate);
  const end = new Date(endDate);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return [];

  const firstMonth = startOfMonth(start);
  const lastMonth = startOfMonth(end);
  const options: PredictionMonthOption[] = [];

  let cursor = addMonths(firstMonth, 2);
  const finalMonth = addMonths(lastMonth, 1);

  while (cursor <= finalMonth) {
    options.push({
      label: cursor.toLocaleDateString("en-NG", { month: "long", year: "numeric" }),
      month: cursor.getMonth() + 1,
      year: cursor.getFullYear(),
      value: `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}`,
    });
    cursor = addMonths(cursor, 1);
  }

  return options;
}
