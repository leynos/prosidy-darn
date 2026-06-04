//! Optional Rust extension for Prosidy Darn.

use pyo3::prelude::*;

/// Return the Rust runtime greeting.
#[pyfunction]
#[must_use]
fn hello() -> &'static str {
    "hello from Rust"
}

/// Python module definition for the optional Rust backend.
///
/// # Errors
/// Returns a Python error if the module cannot be initialized.
#[pymodule]
fn _prosidy_darn_rs(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(hello, module)?)?;
    Ok(())
}
