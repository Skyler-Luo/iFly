<template>
    <!-- No changes to template section -->
</template>

<script>
export default {
    // No changes to component options
};
</script>

<style>
/* No changes to style section */
</style>

<script>
export default {
  methods: {
    selectFlight() {
      this.$emit('select', {
        id: this.flight.id,
        selectedClass: this.selectedClass
      });
    }
  }
};
</script>