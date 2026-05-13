import * as React from "react";
import { cn } from "@/lib/utils";

export interface Column<T> {
  key: string;
  header: React.ReactNode;
  cell: (row: T) => React.ReactNode;
  className?: string;
}

interface Props<T> {
  rows: T[];
  columns: Column<T>[];
  rowKey: (row: T) => string;
  empty?: React.ReactNode;
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({ rows, columns, rowKey, empty, onRowClick }: Props<T>) {
  if (!rows.length && empty) return <>{empty}</>;
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead className="bg-muted/60">
          <tr>
            {columns.map((c) => (
              <th key={c.key} className={cn("px-3 py-2 text-left text-xs font-medium text-muted-foreground", c.className)}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={rowKey(row)}
              onClick={() => onRowClick?.(row)}
              className={cn(
                "border-t border-border",
                onRowClick && "cursor-pointer hover:bg-accent/40",
              )}
            >
              {columns.map((c) => (
                <td key={c.key} className={cn("px-3 py-2 align-top", c.className)}>
                  {c.cell(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
