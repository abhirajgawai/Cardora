/**
 * Formats card names and types for better readability
 * Converts "PREMIERMILES WORLDMASTER" to "Premier Miles World Master"
 */

const KNOWN_WORDS = [
  'PREMIER', 'MILES', 'WORLD', 'MASTER', 'VISA', 'MASTERCARD',
  'PLATINUM', 'GOLD', 'REWARDS', 'CASHBACK', 'CASH', 'BACK',
  'ELITE', 'SIGNATURE', 'INFINITE', 'RESERVE', 'PREFERRED',
  'ALTITUDE', 'LIVE', 'FRESH', 'ONE', 'PLUS', 'PRO', 'SELECT',
  'CLASSIC', 'STANDARD', 'BUSINESS', 'CORPORATE', 'TRAVEL',
  'DINING', 'SHOPPING', 'FIRST', 'BLACK', 'PURPLE', 'GREEN'
];

/**
 * Splits a concatenated word into separate words based on known card terms
 */
function splitCardWords(text: string): string[] {
  const upperText = text.toUpperCase();
  const words: string[] = [];
  let remaining = upperText;

  while (remaining.length > 0) {
    let matched = false;

    // Try to match known words from the beginning
    for (const word of KNOWN_WORDS.sort((a, b) => b.length - a.length)) {
      if (remaining.startsWith(word)) {
        words.push(word);
        remaining = remaining.slice(word.length);
        matched = true;
        break;
      }
    }

    // If no match, take the next character/word
    if (!matched) {
      // Try to find next known word
      let nextWordIndex = remaining.length;
      for (const word of KNOWN_WORDS) {
        const index = remaining.indexOf(word, 1);
        if (index > 0 && index < nextWordIndex) {
          nextWordIndex = index;
        }
      }

      words.push(remaining.slice(0, nextWordIndex));
      remaining = remaining.slice(nextWordIndex);
    }
  }

  return words;
}

/**
 * Converts a word to title case
 */
function toTitleCase(word: string): string {
  if (!word) return '';

  // Keep common acronyms uppercase
  if (['DBS', 'OCBC', 'UOB', 'HSBC', 'ATM', 'EMI'].includes(word.toUpperCase())) {
    return word.toUpperCase();
  }

  return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
}

/**
 * Formats a card type string (e.g., "PREMIERMILES WORLDMASTER" -> "Premier Miles World Master")
 */
export function formatCardType(cardType: string | null | undefined): string {
  if (!cardType) return 'Credit Card';

  // If already has spaces and mixed case, return as is
  if (cardType.includes(' ') && cardType !== cardType.toUpperCase()) {
    return cardType;
  }

  // Remove extra spaces and split by existing spaces
  const segments = cardType.trim().split(/\s+/);
  const allWords: string[] = [];

  for (const segment of segments) {
    // Split concatenated words
    const words = splitCardWords(segment);
    allWords.push(...words);
  }

  // Convert to title case and join
  return allWords
    .map(word => toTitleCase(word))
    .join(' ')
    .trim();
}

/**
 * Formats a bank name (e.g., "CITIBANK" -> "Citibank")
 */
export function formatBankName(bankName: string | null | undefined): string {
  if (!bankName) return 'Unknown Bank';

  // Keep common bank acronyms uppercase
  const upperBank = bankName.toUpperCase();
  if (['DBS', 'OCBC', 'UOB', 'HSBC', 'ANZ', 'BOA', 'SCB'].includes(upperBank)) {
    return upperBank;
  }

  // Convert to title case
  return bankName
    .split(' ')
    .map(word => toTitleCase(word))
    .join(' ');
}

/**
 * Formats a full card name including bank and type
 * E.g., "CITIBANK PREMIERMILES WORLDMASTER" -> "Citibank Premier Miles World Master"
 */
export function formatFullCardName(
  bankName: string | null | undefined,
  cardType: string | null | undefined
): string {
  const formattedBank = formatBankName(bankName);
  const formattedType = formatCardType(cardType);

  if (formattedType === 'Credit Card') {
    return formattedBank;
  }

  return `${formattedBank} ${formattedType}`;
}

/**
 * Formats a card display name (tries card_name first, then falls back to formatted name)
 */
export function formatCardDisplayName(
  cardName: string | null | undefined,
  bankName: string | null | undefined,
  cardType: string | null | undefined,
  lastFourDigits?: string
): string {
  if (cardName) return cardName;

  const fullName = formatFullCardName(bankName, cardType);
  if (lastFourDigits) {
    return `${fullName} (*${lastFourDigits})`;
  }

  return fullName;
}
