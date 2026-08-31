import React from 'react';
import {
  Table, TableBody, TableCaption, TableCell,
  TableHead, TableHeader, TableRow
} from 'cardora';

export const Transactions = () => (
  <div style={{ padding: 24, minWidth: 500 }}>
    <Table>
      <TableCaption>Recent transactions — OCBC 365 Card</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Date</TableHead>
          <TableHead>Merchant</TableHead>
          <TableHead>Category</TableHead>
          <TableHead style={{ textAlign: 'right' }}>Amount (SGD)</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell>15 Jun</TableCell>
          <TableCell>FairPrice Online</TableCell>
          <TableCell>Groceries</TableCell>
          <TableCell style={{ textAlign: 'right' }}>$48.90</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>14 Jun</TableCell>
          <TableCell>Grab Food</TableCell>
          <TableCell>Food & Dining</TableCell>
          <TableCell style={{ textAlign: 'right' }}>$22.50</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>13 Jun</TableCell>
          <TableCell>Shell Petrol</TableCell>
          <TableCell>Transport</TableCell>
          <TableCell style={{ textAlign: 'right' }}>$85.00</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>12 Jun</TableCell>
          <TableCell>Netflix</TableCell>
          <TableCell>Entertainment</TableCell>
          <TableCell style={{ textAlign: 'right' }}>$17.98</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
);
