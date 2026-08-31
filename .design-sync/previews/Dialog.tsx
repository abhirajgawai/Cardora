import React from 'react';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogDescription, DialogFooter, Button
} from 'cardora';

export const Open = () => (
  <div style={{ position: 'relative', height: 380, width: 520 }}>
    <Dialog open>
      <DialogContent style={{ position: 'static', transform: 'none', boxShadow: '0 8px 32px rgba(0,0,0,0.12)' }}>
        <DialogHeader>
          <DialogTitle>Delete transaction?</DialogTitle>
          <DialogDescription>
            This will permanently remove the transaction from your statement history. This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <div style={{ padding: '8px 0', fontSize: 14 }}>
          <strong>Grab Food — $22.50</strong> · 14 Jun 2025
        </div>
        <DialogFooter>
          <Button variant="outline">Cancel</Button>
          <Button variant="destructive">Delete</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
);
