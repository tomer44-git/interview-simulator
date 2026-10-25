# errors.py
# טיפול אחיד בשגיאות שרת.
#
# הבעיה שזה פותר: routers נהגו להחזיר f"...: {str(e)}" ללקוח. הטקסט
# הגולמי של חריגה יכול להכיל נתיבי קבצים, פנימיות של ספריות, מבנה DB —
# ובמקרה אחד בפרויקט הזה הוא הכיל קידומת של מפתח API, שהוצגה בחלון
# שגיאה בדפדפן (commit 4fb59ad).
#
# הפתרון: הפרטים המלאים נרשמים בצד השרת, והלקוח מקבל מזהה קצר בלבד.
# המשתמש מצטט את המזהה, ואנחנו מוצאים את הרשומה המלאה בלוגים.

import logging
from uuid import uuid4

from fastapi import HTTPException

logger = logging.getLogger("interview_simulator")


def server_error(message: str, exc: Exception) -> HTTPException:
    """
    רושם את החריגה המלאה עם traceback ומחזיר HTTPException "עיוור".

    שימוש — תמיד מתוך בלוק except, אחרת לא ייתפס traceback:

        except Exception as e:
            raise server_error("Persona build failed", e)

    הלקוח מקבל:  "Persona build failed (ref: a3f9c1)"
    הלוג מקבל:   את ההודעה, המזהה, וה-traceback המלא
    """
    ref = uuid4().hex[:8]

    # logger.exception מצרף את ה-traceback הנוכחי — לכן חובה לקרוא מ-except
    logger.exception("%s [ref=%s] %s: %s", message, ref, type(exc).__name__, exc)

    return HTTPException(status_code=500, detail=f"{message} (ref: {ref})")
