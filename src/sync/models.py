from django.db import models


class SyncLog(models.Model):
    ran_at = models.DateTimeField(auto_now_add=True)
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            f"Sync at {self.ran_at}:"
            f"{self.created_count} created,"
            f"{self.updated_count} updated"
        )
    
    class Meta:
        ordering = ["-ran_at"]
