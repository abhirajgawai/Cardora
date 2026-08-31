import React from 'react';
import {
  Command, CommandInput, CommandList, CommandEmpty,
  CommandGroup, CommandItem, CommandSeparator
} from 'cardora';

export const SearchPalette = () => (
  <div style={{ padding: 24, width: 380 }}>
    <Command style={{ border: '1px solid var(--border)', borderRadius: 8 }}>
      <CommandInput placeholder="Search transactions, cards, categories..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Transactions">
          <CommandItem>FairPrice Online · $48.90</CommandItem>
          <CommandItem>Grab Food · $22.50</CommandItem>
          <CommandItem>Netflix · $17.98</CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Categories">
          <CommandItem>Groceries</CommandItem>
          <CommandItem>Food &amp; Dining</CommandItem>
          <CommandItem>Entertainment</CommandItem>
        </CommandGroup>
      </CommandList>
    </Command>
  </div>
);
