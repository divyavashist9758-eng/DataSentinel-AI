/**
 * Safely extract human-readable error messages from API responses.
 * Handles string details, FastAPI Pydantic validation error arrays, and Axios error objects.
 */
export function extractErrorMessage(err: any, fallbackMessage = 'An unexpected error occurred'): string {
  if (!err) return fallbackMessage;

  const detail = err.response?.data?.detail;

  if (typeof detail === 'string' && detail.trim() !== '') {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item: any) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object') {
          const loc = Array.isArray(item.loc) ? item.loc.slice(1).join('.') : '';
          const msg = item.msg || item.message || JSON.stringify(item);
          return loc ? `${loc}: ${msg}` : msg;
        }
        return String(item);
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join('; ');
    }
  }

  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  if (err.response?.data?.message && typeof err.response.data.message === 'string') {
    return err.response.data.message;
  }

  if (err.message && typeof err.message === 'string') {
    return err.message;
  }

  return fallbackMessage;
}
